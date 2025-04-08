# Fault Code Interpreter Bot

A Telegram bot that helps technical teams interpret fault codes without needing to contact an engineer. The bot reads from a database of fault codes and provides instant explanations.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Telegram bot token:
```
TELEGRAM_TOKEN=your_bot_token_here
```

3. Update the fault codes database in `data/fault_codes.csv`

4. Run the bot:
```bash
python src/bot.py
```

## Updating Fault Codes
To add or modify fault codes, simply update the `data/fault_codes.csv` file. The format is:
```
code,description
F001,"Description of fault code F001"
F002,"Description of fault code F002"
```

## Features
- Quick fault code lookup
- Easy to update fault code database
- Available 24/7 for instant responses