#!/usr/bin/env python3
"""
Log Analyzer for Telegram Bot
Analyzes bot logs to provide insights on usage, performance, and errors.
"""

import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import argparse

def analyze_logs(log_dir='logs', days=2):
    """Analyze bot logs for the specified number of days."""
    
    # Get log files for the specified days
    log_files = []
    error_files = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y%m%d')
        
        bot_log = os.path.join(log_dir, f'bot_{date_str}.log')
        error_log = os.path.join(log_dir, f'errors_{date_str}.log')
        
        if os.path.exists(bot_log):
            log_files.append(bot_log)
        if os.path.exists(error_log):
            error_files.append(error_log)
    
    if not log_files and not error_files:
        print(f"No log files found in {log_dir} for the last {days} days")
        return
    
    # Analysis containers
    stats = {
        'total_requests': 0,
        'total_responses': 0,
        'total_errors': 0,
        'slow_responses': 0,
        'commands': defaultdict(int),
        'users': defaultdict(int),
        'response_times': [],
        'errors': [],
        'catl_lookups': 0,
        'fault_lookups': 0,
        'fault_success': 0,
        'fault_not_found': 0,
        'catl_success': 0,
        'catl_invalid': 0
    }
    
    # Process bot logs
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                analyze_log_line(line, stats)
    
    # Process error logs
    for error_file in error_files:
        with open(error_file, 'r', encoding='utf-8') as f:
            for line in f:
                analyze_error_line(line, stats)
    
    # Generate report
    generate_report(stats, days)

def analyze_log_line(line, stats):
    """Analyze a single log line."""
    
    # Request tracking
    if 'REQUEST - User:' in line:
        stats['total_requests'] += 1
        user_match = re.search(r'User: (\d+)', line)
        if user_match:
            stats['users'][user_match.group(1)] += 1
    
    # Response tracking
    elif 'RESPONSE - User:' in line:
        stats['total_responses'] += 1
        time_match = re.search(r'Response time: ([\d.]+)ms', line)
        if time_match:
            response_time = float(time_match.group(1))
            stats['response_times'].append(response_time)
    
    # Slow response tracking
    elif 'SLOW_RESPONSE' in line:
        stats['slow_responses'] += 1
    
    # Command tracking
    elif 'COMMAND -' in line:
        if '/start' in line:
            stats['commands']['/start'] += 1
        elif '/help' in line:
            stats['commands']['/help'] += 1
        elif '/list' in line:
            stats['commands']['/list'] += 1
        elif 'CATL' in line:
            stats['commands']['CATL'] += 1
            stats['catl_lookups'] += 1
    
    # CATL specific tracking
    elif 'CATL_SUCCESS' in line:
        stats['catl_success'] += 1
    elif 'CATL_INVALID' in line:
        stats['catl_invalid'] += 1
    
    # Fault code tracking
    elif 'FAULT_LOOKUP' in line:
        stats['fault_lookups'] += 1
    elif 'FAULT_SUCCESS' in line:
        stats['fault_success'] += 1
    elif 'FAULT_NOT_FOUND' in line:
        stats['fault_not_found'] += 1

def analyze_error_line(line, stats):
    """Analyze a single error log line."""
    stats['total_errors'] += 1
    stats['errors'].append(line.strip())

def generate_report(stats, days):
    """Generate a comprehensive report."""
    
    print("="*60)
    print(f"TELEGRAM BOT LOG ANALYSIS REPORT")
    print(f"Period: Last {days} day(s)")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Overall statistics
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Total Responses: {stats['total_responses']}")
    print(f"   Total Errors: {stats['total_errors']}")
    print(f"   Success Rate: {(stats['total_responses'] - stats['total_errors']) / max(stats['total_responses'], 1) * 100:.1f}%")
    
    # Performance metrics
    if stats['response_times']:
        avg_response_time = sum(stats['response_times']) / len(stats['response_times'])
        max_response_time = max(stats['response_times'])
        min_response_time = min(stats['response_times'])
        
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   Average Response Time: {avg_response_time:.2f}ms")
        print(f"   Max Response Time: {max_response_time:.2f}ms")
        print(f"   Min Response Time: {min_response_time:.2f}ms")
        print(f"   Slow Responses (>1s): {stats['slow_responses']}")
    
    # Command usage
    print(f"\n🔧 COMMAND USAGE:")
    for command, count in sorted(stats['commands'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {command}: {count}")
    
    # User activity
    print(f"\n👥 USER ACTIVITY:")
    print(f"   Unique Users: {len(stats['users'])}")
    if stats['users']:
        top_users = sorted(stats['users'].items(), key=lambda x: x[1], reverse=True)[:5]
        for user_id, count in top_users:
            print(f"   User {user_id}: {count} requests")
    
    # CATL specific metrics
    if stats['catl_lookups'] > 0:
        catl_success_rate = stats['catl_success'] / stats['catl_lookups'] * 100
        print(f"\n🔋 CATL LOOKUP METRICS:")
        print(f"   Total CATL Requests: {stats['catl_lookups']}")
        print(f"   Successful Lookups: {stats['catl_success']}")
        print(f"   Invalid Inputs: {stats['catl_invalid']}")
        print(f"   Success Rate: {catl_success_rate:.1f}%")
    
    # Fault code metrics
    if stats['fault_lookups'] > 0:
        fault_success_rate = stats['fault_success'] / stats['fault_lookups'] * 100
        print(f"\n🔍 FAULT CODE METRICS:")
        print(f"   Total Fault Code Requests: {stats['fault_lookups']}")
        print(f"   Successful Lookups: {stats['fault_success']}")
        print(f"   Not Found: {stats['fault_not_found']}")
        print(f"   Success Rate: {fault_success_rate:.1f}%")
    
    # Recent errors
    if stats['errors']:
        print(f"\n❌ RECENT ERRORS (Last 5):")
        for error in stats['errors'][-5:]:
            print(f"   {error}")
    
    print("\n" + "="*60)

def main():
    parser = argparse.ArgumentParser(description='Analyze Telegram Bot logs')
    parser.add_argument('--days', type=int, default=2, help='Number of days to analyze (default: 2)')
    parser.add_argument('--log-dir', default='logs', help='Log directory (default: logs)')
    
    args = parser.parse_args()
    analyze_logs(args.log_dir, args.days)

if __name__ == '__main__':
    main() 