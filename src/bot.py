import logging
import os
import pandas as pd
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from float_lookup import lookup_float_value

# Load environment variables
load_dotenv()

# ANSI color codes
RED = '\033[91m'
RESET = '\033[0m'

# Configure logging with color
class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels"""
    
    def format(self, record):
        if record.levelno >= logging.ERROR:
            record.msg = f"{RED}{record.msg}{RESET}"
        return super().format(record)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create console handler with custom formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(console_handler)

# Load fault codes database
def load_fault_codes():
    try:
        logging.info("="*50)
        logging.info("Starting fault codes database load")
        
        # Initialize separate dictionaries for each product
        q1_dict = {}
        q2_dict = {}
        
        # Load Q1 product codes
        try:
            logging.info("Loading Q1 product codes...")
            df_q1 = pd.read_csv('data/DTC_Q1.csv', delimiter=';', encoding='latin-1')
            logging.info(f"Q1 CSV loaded: {len(df_q1)} rows")
        except Exception as e:
            logging.error(f"Failed to load Q1 CSV file: {str(e)}")
            return {'Q1': {}, 'Q2': {}}
        
        # Process Q1 codes
        for idx, row in df_q1.iterrows():
            try:
                entry = {
                    'description': row['Descripcion Corta'],
                    'system': row['System'],
                    'level': row['Nivel'],
                    'product': 'Q1'
                }
                q1_dict[row['Codigo'].upper()] = entry
                q1_dict[str(row['Codigo Decimal'])] = entry
            except Exception as row_error:
                logging.error(f"Error processing Q1 row {idx + 1}: {row_error}")
                logging.error(f"Problematic row data: {row.to_dict()}")
        
        # Load Q2 product codes
        try:
            logging.info("Loading Q2 product codes...")
            df_q2 = pd.read_csv('data/DTC_Q2.csv', delimiter=';', encoding='latin-1')
            logging.info(f"Q2 CSV loaded: {len(df_q2)} rows")
        except Exception as e:
            logging.error(f"Failed to load Q2 CSV file: {str(e)}")
            return {'Q1': q1_dict, 'Q2': {}}
        
        # Process Q2 codes
        for idx, row in df_q2.iterrows():
            try:
                entry = {
                    'description': row['Descripcion Corta'],
                    'system': row['System'],
                    'level': row['Nivel'],
                    'product': 'Q2'
                }
                q2_dict[row['Codigo'].upper()] = entry
                q2_dict[str(row['Codigo Decimal'])] = entry
            except Exception as row_error:
                logging.error(f"Error processing Q2 row {idx + 1}: {row_error}")
                logging.error(f"Problematic row data: {row.to_dict()}")
        
        logging.info(f"Total Q1 codes loaded: {len(q1_dict)}")
        logging.info(f"Total Q2 codes loaded: {len(q2_dict)}")
        logging.info("="*50)
        return {'Q1': q1_dict, 'Q2': q2_dict}
        
    except Exception as e:
        logging.error("="*50)
        logging.error("Critical error in fault codes database:")
        logging.error(f"Error type: {type(e).__name__}")
        logging.error(f"Error message: {str(e)}")
        logging.error("="*50)
        return {'Q1': {}, 'Q2': {}}

fault_codes = load_fault_codes()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome to the Fault Code Interpreter Bot!\n\n"
        "To look up a fault code, send a message in this format:\n"
        "<product> <code>\n\n"
        "Available products:\n"
        "- Q1\n"
        "- Q2\n\n"
        "Examples:\n"
        "Q1 16897\n"
        "Q2 0x4201\n\n"
        "For CATL float value lookup:\n"
        "CATL <value>\n"
        "Example: CATL 3.247\n\n"
        "Available commands:\n"
        "/start - Show this welcome message\n"
        "/help - Show help information\n"
        "/list - List all available fault codes"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "To use this bot, send a message in this format:\n"
        "<product> <code>\n\n"
        "Available products:\n"
        "- Q1\n"
        "- Q2\n\n"
        "Examples:\n"
        "Q1 16897\n"
        "Q2 0x4201\n\n"
        "The bot will respond with:\n"
        "📝 Fault Code: The code you entered\n"
        "🔍 Description: What the code means\n"
        "⚙️ System: Which system the code belongs to\n"
        "⚠️ Severity: The severity level\n"
        "🏭 Product: The product you specified\n\n"
        "For CATL float value lookup:\n"
        "CATL <value>\n"
        "Example: CATL 3.247\n"
        "Valid range: 2.800 - 3.700\n\n"
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
    
    # Create separate lists for Q1 and Q2 codes
    q1_codes = []
    q2_codes = []
    
    # Process Q1 codes
    for code, info in fault_codes['Q1'].items():
        if code.isdigit():  # Only show decimal codes to avoid duplicates
            q1_codes.append(f"{code} - {info['description']}")
    
    # Process Q2 codes
    for code, info in fault_codes['Q2'].items():
        if code.isdigit():  # Only show decimal codes to avoid duplicates
            q2_codes.append(f"{code} - {info['description']}")
    
    # Sort the lists
    q1_codes.sort()
    q2_codes.sort()
    
    # Limit the number of codes shown
    max_codes = 5
    if len(q1_codes) > max_codes:
        q1_codes = q1_codes[:max_codes]
        q1_codes.append(f"... and {len(fault_codes['Q1']) - max_codes} more Q1 codes")
    
    if len(q2_codes) > max_codes:
        q2_codes = q2_codes[:max_codes]
        q2_codes.append(f"... and {len(fault_codes['Q2']) - max_codes} more Q2 codes")
    
    # Create the response message
    codes_list = "Available fault codes:\n\n"
    
    if q1_codes:
        codes_list += "Q1 Product Codes:\n"
        for code in q1_codes:
            codes_list += f"{code}\n"
        codes_list += "\n"
    
    if q2_codes:
        codes_list += "Q2 Product Codes:\n"
        for code in q2_codes:
            codes_list += f"{code}\n"
    
    codes_list += "\nTo get detailed information about a specific code, send:\n"
    codes_list += "<product> <code>"
    
    await update.message.reply_text(codes_list)

async def catl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle CATL command for float value lookup."""
    message = update.message.text.strip()
    
    # Check if it's a CATL command
    if not message.upper().startswith('CATL'):
        return False
    
    # Extract the value after CATL
    parts = message.split()
    if len(parts) != 2:
        response = (
            "❌ Invalid CATL format. Please use:\n"
            "CATL <value>\n\n"
            "Examples:\n"
            "CATL 3.247\n"
            "CATL 3.242\n\n"
            "Valid range: 2.800 - 3.700"
        )
        await update.message.reply_text(response)
        return True
    
    command, value = parts
    
    # Look up the float value
    result = lookup_float_value(value)
    
    if result is not None:
        response = (
            f"🔍 CATL Lookup Result:\n"
            f"📥 Input Value: {value}\n"
            f"📤 Return Value: {result}"
        )
    else:
        response = (
            f"❌ Invalid input value: {value}\n\n"
            "Please provide a valid number between 2.800 and 3.700\n\n"
            "Examples:\n"
            "CATL 3.247\n"
            "CATL 2.932"
        )
    
    await update.message.reply_text(response)
    return True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and look up fault codes."""
    message = update.message.text.strip()
    
    # Check if it's a CATL command first
    if message.upper().startswith('CATL'):
        await catl_command(update, context)
        return
    
    # Convert to uppercase for fault code processing
    message = message.upper()
    
    # Split message into product and code
    parts = message.split()
    if len(parts) != 2:
        response = (
            "❌ Invalid format. Please use:\n"
            "<product> <code>\n\n"
            "Available products:\n"
            "- Q1\n"
            "- Q2\n\n"
            "Examples:\n"
            "Q1 16897\n"
            "Q2 0x4201\n\n"
            "Or use CATL command:\n"
            "CATL 3.247"
        )
        await update.message.reply_text(response)
        return
    
    product, code = parts
    
    # Validate product
    if product not in ['Q1', 'Q2']:
        response = (
            "❌ Invalid product. Please use one of the available products:\n"
            "- Q1\n"
            "- Q2\n\n"
            "Examples:\n"
            "Q1 16897\n"
            "Q2 0x4201"
        )
        await update.message.reply_text(response)
        return
    
    # Add 0x prefix if it's a hex code without it
    if len(code) == 4 and all(c in '0123456789ABCDEF' for c in code):
        code = '0x' + code
    
    # Look up the code in the appropriate product dictionary
    product_dict = fault_codes[product]
    if code in product_dict:
        fault_info = product_dict[code]
        response = (
            f"📝 Fault Code: {code}\n"
            f"🔍 Description: {fault_info['description']}\n"
            f"⚙️ System: {fault_info['system']}\n"
            f"⚠️ Severity: {fault_info['level']}\n"
            f"🏭 Product: {fault_info['product']}"
        )
    else:
        response = (
            f"❌ Sorry, I couldn't find code {code} for {product}.\n\n"
            "Please enter either:\n"
            "- Hex code (e.g., 0x4201)\n"
            "- Decimal code (e.g., 16897)\n\n"
            "Use /list to see available codes.\n\n"
            "Or use CATL command for float value lookup:\n"
            "CATL 3.247"
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