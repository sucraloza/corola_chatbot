# Telegram Bot Logging System

This document explains the logging system implemented in the Telegram Bot for debugging and monitoring purposes.

## Log Files

The bot creates two types of log files in the `logs/` directory:

### 1. Main Bot Log (`logs/bot_YYYYMMDD.log`)
Contains all bot activities including:
- User requests and responses
- Command executions
- Performance metrics
- Successful operations

### 2. Error Log (`logs/errors_YYYYMMDD.log`)
Contains only error messages for easier debugging.

## Log Categories

### Request/Response Tracking
- `REQUEST - User: {user_id} (@{username}) - Message: '{message}'`
- `RESPONSE - User: {user_id} - Response time: {time}ms - Success`
- `SLOW_RESPONSE - User: {user_id} - Response time: {time}ms` (for responses >1s)

### Command Usage
- `COMMAND - /start executed`
- `COMMAND - /help executed`
- `COMMAND - /list executed`
- `COMMAND - CATL lookup requested`

### CATL Lookup Operations
- `CATL_LOOKUP - Input value: {value}`
- `CATL_SUCCESS - Input: {value} -> Result: {result}`
- `CATL_INVALID - Input value: {value} is invalid`

### Fault Code Operations
- `FAULT_LOOKUP - Product: {product}, Code: {code}`
- `FAULT_SUCCESS - Product: {product}, Code: {code} -> Found`
- `FAULT_NOT_FOUND - Product: {product}, Code: {code} -> Not found`

### System Events
- `BOT_STARTUP - Starting Telegram Bot`
- `BOT_STARTUP - Log files: logs/bot_{date}.log`
- `BOT_STARTUP - Token found, building application`
- `BOT_STARTUP - Adding command handlers`
- `BOT_STARTUP - Starting polling`

## Using the Log Analyzer

The `src/log_analyzer.py` script provides comprehensive analysis of bot logs:

### Basic Usage
```bash
# Analyze today's logs
python src/log_analyzer.py

# Analyze last 3 days
python src/log_analyzer.py --days 3

# Analyze logs from custom directory
python src/log_analyzer.py --log-dir /path/to/logs
```

### Sample Output
```
============================================================
TELEGRAM BOT LOG ANALYSIS REPORT
Period: Last 1 day(s)
Generated: 2024-01-15 14:30:25
============================================================

📊 OVERALL STATISTICS:
   Total Requests: 25
   Total Responses: 25
   Total Errors: 0
   Success Rate: 100.0%

⚡ PERFORMANCE METRICS:
   Average Response Time: 245.67ms
   Max Response Time: 1200.45ms
   Min Response Time: 89.23ms
   Slow Responses (>1s): 2

🔧 COMMAND USAGE:
   CATL: 12
   /start: 5
   /help: 3
   /list: 2

👥 USER ACTIVITY:
   Unique Users: 3
   User 123456789: 15 requests
   User 987654321: 8 requests
   User 555666777: 2 requests

🔋 CATL LOOKUP METRICS:
   Total CATL Requests: 12
   Successful Lookups: 11
   Invalid Inputs: 1
   Success Rate: 91.7%

🔍 FAULT CODE METRICS:
   Total Fault Code Requests: 8
   Successful Lookups: 7
   Not Found: 1
   Success Rate: 87.5%
============================================================
```

## Monitoring Tips

### 1. Check for Slow Responses
Look for `SLOW_RESPONSE` entries in the logs. These indicate responses taking longer than 1 second.

### 2. Monitor Error Rates
Check the error log file for any recurring issues or patterns.

### 3. Track User Activity
Use the log analyzer to see which users are most active and what commands they use most.

### 4. Performance Monitoring
Monitor average response times to ensure the bot remains responsive.

### 5. Success Rates
Track success rates for both CATL lookups and fault code lookups to identify potential issues.

## Log Rotation

Logs are automatically created daily with the format `YYYYMMDD`. Old logs are not automatically deleted, so you may want to implement log rotation for long-term deployments.

## Troubleshooting

### Common Issues

1. **No logs being created**: Check if the `logs/` directory exists and has write permissions
2. **Missing log entries**: Ensure the bot is running with the updated logging configuration
3. **Permission errors**: Make sure the bot process has write access to the logs directory

### Debug Mode

To enable more verbose logging, you can modify the log level in `bot.py`:
```python
logger.setLevel(logging.DEBUG)  # Change from logging.INFO
```

## Integration with Monitoring Systems

The structured log format makes it easy to integrate with monitoring systems like:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana
- Prometheus
- Custom monitoring dashboards

The log analyzer can be run as a cron job to generate regular reports or integrated into monitoring dashboards. 