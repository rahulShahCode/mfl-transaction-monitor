#!/usr/bin/env python3
"""
Set the last run time for the transaction monitor
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from datetime import datetime, timezone, timedelta

def set_last_run_time(hours_ago=None, specific_date=None):
    """Set the last run time for the transaction monitor"""
    
    if hours_ago:
        last_run_time = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    elif specific_date:
        try:
            last_run_time = datetime.strptime(specific_date, "%Y-%m-%d %H:%M:%S")
            last_run_time = last_run_time.replace(tzinfo=timezone.utc)
        except ValueError:
            print("❌ Invalid date format. Use 'YYYY-MM-DD HH:MM:SS'")
            return False
    else:
        print("❌ Please specify either hours_ago or specific_date")
        return False
    
    data = {"last_run_time": last_run_time.isoformat()}
    
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/transaction_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Set last run time to: {last_run_time}")
        print(f"   This means the next run will check transactions since this time")
        return True
        
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python set_last_run.py --hours 24          # Set to 24 hours ago")
        print("  python set_last_run.py --date '2024-12-01 00:00:00'  # Set to specific date")
        print("  python set_last_run.py --reset             # Reset to 24 hours ago")
        return
    
    if sys.argv[1] == "--hours" and len(sys.argv) > 2:
        hours = int(sys.argv[2])
        set_last_run_time(hours_ago=hours)
    elif sys.argv[1] == "--date" and len(sys.argv) > 2:
        date_str = sys.argv[2]
        set_last_run_time(specific_date=date_str)
    elif sys.argv[1] == "--reset":
        set_last_run_time(hours_ago=24)
    else:
        print("❌ Invalid arguments")

if __name__ == "__main__":
    main()