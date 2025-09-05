#!/usr/bin/env python3
"""
MFL transaction monitor - catches people picking up players after games start
"""

import argparse
import asyncio
import sys
from src.mfl_monitor.core.analyzer import TransactionAnalyzer
from src.mfl_monitor.core.scheduler import TransactionScheduler
from src.mfl_monitor.utils.config import Config
from src.mfl_monitor.apis.discord_bot import DiscordNotifier
from src.mfl_monitor.apis.mfl_api import MFLAPI
from src.mfl_monitor.apis.odds_api import OddsAPIClient
from src.mfl_monitor.apis.espn_api import ESPNAPIClient

def test_configuration():
    """Test if everything is set up correctly"""
    print("Testing configuration...")
    
    if not Config.validate():
        return False
    
    print("✅ All required environment variables are set")
    
    # Test MFL API connection
    print("Testing MFL API connection...")
    try:
        mfl_api = MFLAPI()
        transactions = mfl_api.get_transactions()
        print(f"✅ MFL API connection successful - found {len(transactions)} recent transactions")
    except Exception as e:
        print(f"❌ MFL API connection failed: {e}")
        return False
    
    # Test ESPN API connection (primary)
    print("Testing ESPN API connection...")
    try:
        espn_client = ESPNAPIClient()
        if not espn_client.test_api_connection():
            print("❌ ESPN API connection failed")
            return False
        print("✅ ESPN API connection successful")
    except Exception as e:
        print(f"❌ ESPN API connection failed: {e}")
        return False
    
    # Test The Odds API connection (fallback)
    print("Testing The Odds API connection...")
    try:
        odds_client = OddsAPIClient()
        if not odds_client.test_api_connection():
            print("❌ The Odds API connection failed")
            return False
        print("✅ The Odds API connection successful")
    except Exception as e:
        print(f"❌ The Odds API connection failed: {e}")
        return False
    
    # Test Discord connection
    print("Testing Discord connection...")
    try:
        asyncio.run(DiscordNotifier().send_notification("🧪 Test message from MFL Transaction Monitor"))
        print("✅ Discord connection successful")
    except Exception as e:
        print(f"❌ Discord connection failed: {e}")
        return False
    
    print("✅ All tests passed! Configuration is valid.")
    return True

async def run_single_check(force=False):
    """Run a single transaction check"""
    print("Running single transaction check...")
    scheduler = TransactionScheduler()
    await scheduler.run_check(force=force)

def main():
    parser = argparse.ArgumentParser(
        description='MFL Transaction Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --test          # Test configuration
  python main.py --once          # Run once (respects time restrictions)
  python main.py --force         # Force run (ignores time restrictions)
  python main.py                 # Run continuously with scheduling
        """
    )
    
    parser.add_argument('--once', action='store_true', 
                       help='Run a single check instead of scheduling')
    parser.add_argument('--test', action='store_true', 
                       help='Test configuration and connections')
    parser.add_argument('--force', action='store_true', 
                       help='Force run ignoring time restrictions')
    
    args = parser.parse_args()
    
    if args.test:
        success = test_configuration()
        sys.exit(0 if success else 1)
    
    if args.once or args.force:
        asyncio.run(run_single_check(force=args.force))
    else:
        # Run the scheduler
        scheduler = TransactionScheduler()
        scheduler.schedule_checks()

if __name__ == "__main__":
    main()