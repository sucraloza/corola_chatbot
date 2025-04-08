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
        df = pd.read_csv('data/fault_codes.csv')
        return dict(zip(df['code'], df['description']))
    except Exception as e:
        logging.error(f"Error loading fault codes: {e}")
        return {}

fault_codes = load_fault_codes()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome to the Fault Code Interpreter Bot!\n\n"
        "Simply send me a fault code (e.g., F001) and I'll tell you what it means.\n\n"
        "Available commands:\n"
        "/start - Show this welcome message\n"
        "/help - Show help information\n"
        "/list - List all available fault codes"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "To use this bot, simply send a fault code and I'll provide its explanation.\n\n"
        "For example, send 'F001' and I'll tell you what that fault code means.\n\n"
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
    
    codes_list = "Available fault codes:\n\n"
    for code in sorted(fault_codes.keys()):
        codes_list += f"{code}\n"
    await update.message.reply_text(codes_list)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and look up fault codes."""
    message = update.message.text.strip().upper()
    
    if message in fault_codes:
        response = f"📝 Fault Code: {message}\n\n🔍 Explanation: {fault_codes[message]}"
    else:
        response = (
            "❌ Sorry, I couldn't find that fault code.\n\n"
            "Please make sure you've entered a valid code (e.g., F001).\n"
            "Use /list to see all available codes."
        )
    
    await update.message.reply_text(response)

def main():
    """Start the bot."""
    # Create the Application
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logging.error("No TELEGRAM_TOKEN found in environment variables!")
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