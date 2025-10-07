# Fault Code Interpreter Bot

A Telegram bot that helps technical teams interpret fault codes without needing to contact an engineer. The bot reads from a database of fault codes and provides instant explanations.

## Features
- **Multi-Product Support**: Q1, Q2, T2, Q3 fault codes
- **CATL Lookup**: Float value to SOC conversion
- **Quick Lookup**: Instant fault code interpretation
- **24/7 Availability**: Always ready to help
- **User-Friendly**: Emoji-enhanced responses

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Telegram bot token:
```
TELEGRAM_TOKEN=your_bot_token_here
```

3. Run the bot:
```bash
python src/bot.py
```

## Service Management (Raspberry Pi)

The bot runs as a systemd service called `corola-bot`. Use these commands to manage it:

### Check Status
```bash
sudo systemctl status corola-bot
```

### Start the Service
```bash
sudo systemctl start corola-bot
```

### Stop the Service
```bash
sudo systemctl stop corola-bot
```

### Restart the Service
```bash
sudo systemctl restart corola-bot
```

### Enable Auto-Start on Boot
```bash
sudo systemctl enable corola-bot
```

### Disable Auto-Start on Boot
```bash
sudo systemctl disable corola-bot
```

### View Logs
```bash
# View recent logs
sudo journalctl -u corola-bot -n 50

# Follow logs in real-time
sudo journalctl -u corola-bot -f

# View logs from today
sudo journalctl -u corola-bot --since today
```

## Updating the Bot

When you update the code, restart the service:
```bash
sudo systemctl restart corola-bot
```

## Available Products
- **Q1**: 376 fault codes
- **Q2**: 426 fault codes  
- **T2**: 528 fault codes
- **Q3**: 366 fault codes

## Usage Examples
```
Q1 16897
Q2 0x4201
T2 14592
Q3 17445
CATL 3.247
```