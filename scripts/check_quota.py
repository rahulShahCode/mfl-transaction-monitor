#!/usr/bin/env python3
"""
Check The Odds API Quota Usage
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mfl_monitor.utils.quota import QuotaManager

def check_quota_status():
    """Check current quota status"""
    print("📊 The Odds API Quota Status")
    print("=" * 40)
    
    quota_manager = QuotaManager()
    quota_data = quota_manager.get_quota_status()
    
    print(f"Requests Used: {quota_data.get('requests_used', 0)}")
    print(f"Requests Remaining: {quota_data.get('requests_remaining', 0)}")
    print(f"Last Reset: {quota_data.get('last_reset', 'Never')}")
    
    # Daily usage
    daily_usage = quota_data.get('daily_usage', {})
    if daily_usage:
        print("\n📅 Daily Usage:")
        for date, count in sorted(daily_usage.items()):
            print(f"  {date}: {count} requests")
    
    # Quota warnings
    remaining = quota_data.get('requests_remaining', 0)
    if remaining <= 0:
        print("\n❌ NO QUOTA REMAINING!")
        print("You need to wait for quota reset or upgrade your plan")
    elif remaining < 10:
        print(f"\n⚠️  LOW QUOTA: {remaining} requests remaining")
        print("Consider reducing API calls or upgrading your plan")
    elif remaining < 50:
        print(f"\n⚠️  MODERATE QUOTA: {remaining} requests remaining")
    else:
        print(f"\n✅ Good quota status: {remaining} requests remaining")
    
    # Usage recommendations
    print("\n💡 Usage Recommendations:")
    print("- Each transaction check uses 1-2 API calls")
    print("- Running every hour = ~24-48 calls per day")
    print("- Free tier: 500 requests per month")
    print("- Consider running every 2-3 hours to save quota")

def main():
    check_quota_status()
    
    print("\n🔧 To reduce quota usage:")
    print("1. Run less frequently (every 2-3 hours instead of every hour)")
    print("2. Use mock schedule when no games are scheduled")
    print("3. Cache game times for multiple hours")
    print("4. Upgrade to paid plan for more quota")

if __name__ == "__main__":
    main()