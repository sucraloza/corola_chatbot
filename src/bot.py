import logging
import os
import pandas as pd
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load fault codes database
def load_fault_codes():
    try:
        logging.info("Attempting to load CSV file...")
        df = pd.read_csv('data/DTC_Q1.csv', delimiter=';', encoding='latin-1')
        
        logging.info(f"CSV loaded successfully. Found {len(df)} rows")
        logging.info(f"Columns found: {df.columns.tolist()}")
        
        # Create a dictionary with both hex and decimal codes as keys
        fault_dict = {}
        for _, row in df.iterrows():
            try:
                # Add hex code entry
                fault_dict[row['Codigo'].upper()] = {
                    'description': row['Descripcion Corta'],
                    'system': row['System'],
                    'level': row['Nivel']
                }
                # Add decimal code entry
                fault_dict[str(row['Codigo Decimal'])] = {
                    'description': row['Descripcion Corta'],
                    'system': row['System'],
                    'level': row['Nivel']
                }
            except Exception as row_error:
                logging.error(f"\033[91mError processing row: {row}\nError: {row_error}\033[0m")
                
        logging.info(f"Dictionary created with {len(fault_dict)} entries")
        return fault_dict
    except Exception as e:
        logging.error(f"\033[91mError loading fault codes: {e}\033[0m")
        # Print more details about the error
        logging.error(f"\033[91mFull error details: {str(e)}\033[0m")
        return {}

fault_codes = load_fault_codes()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome to the Fault Code Interpreter Bot!\n\n"
        "You can send me either:\n"
        "- Hex code (e.g., 0x4201)\n"
        "- Decimal code (e.g., 16897)\n\n"
        "Example response format:\n"
        "📝 Fault Code: 16897\n"
        "🔍 Description: Las Baterías activaron una bandera de falla\n"
        "⚙️ System: Battery\n"
        "⚠️ Severity: Nivel 7\n\n"
        "Available commands:\n"
        "/start - Show this welcome message\n"
        "/help - Show help information\n"
        "/list - List all available fault codes"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "To use this bot, send a fault code in either format:\n"
        "- Hex format: 0x4201\n"
        "- Decimal format: 16897\n\n"
        "Example response format:\n"
        "📝 Fault Code: 16897\n"
        "🔍 Description: Las Baterías activaron una bandera de falla\n"
        "⚙️ System: Battery\n"
        "⚠️ Severity: Nivel 7\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/list - Show all available fault codes"
    )
    await update.message.reply_text(help_text)

async def list_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available fault codes."""
    if not fault_codes:
        await update.message.reply_text("No fault codes available at the moment.")
        return
    
    # Only show decimal codes to avoid duplicates
    decimal_codes = sorted([code for code in fault_codes.keys() if code.isdigit()])
    if len(decimal_codes) > 5:  # Limit the number of codes shown
        codes_list = "First 5 available fault codes (use specific code for details):\n\n"
        decimal_codes = decimal_codes[:5]
    else:
        codes_list = "Available fault codes:\n\n"
    
    for code in decimal_codes:
        codes_list += f"{code} - {fault_codes[code]['description']}\n"
    await update.message.reply_text(codes_list)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and look up fault codes."""
    message = update.message.text.strip().upper()
    
    # Add 0x prefix if it's a hex code without it
    if len(message) == 4 and all(c in '0123456789ABCDEF' for c in message):
        message = '0x' + message
    
    if message in fault_codes:
        fault_info = fault_codes[message]
        response = (
            f"📝 Fault Code: {message}\n"
            f"🔍 Description: {fault_info['description']}\n"
            f"⚙️ System: {fault_info['system']}\n"
            f"⚠️ Severity: {fault_info['level']}"
        )
    else:
        response = (
            "❌ Sorry, I couldn't find that fault code.\n\n"
            "Please enter either:\n"
            "- Hex code (e.g., 0x4201)\n"
            "- Decimal code (e.g., 16897)\n\n"
            "Use /list to see available codes."
        )
    
    await update.message.reply_text(response)

def main():
    """Start the bot."""
    # Create the Application
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logging.error("\033[91mNo TELEGRAM_TOKEN found in environment variables!\033[0m")
        return

    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_codes))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 