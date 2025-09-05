#!/usr/bin/env python3
"""
Configuration validation script
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mfl_monitor.utils.config import Config
from src.mfl_monitor.apis.mfl_api import MFLAPI
from src.mfl_monitor.apis.odds_api import OddsAPIClient
from src.mfl_monitor.apis.discord_bot import DiscordNotifier
import asyncio

def validate_configuration():
    """Validate complete configuration"""
    print("🔧 MFL Transaction Monitor - Configuration Validation")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Environment Variables:")
    if Config.validate():
        print("   ✅ All required environment variables are set")
    else:
        print("   ❌ Missing required environment variables")
        return False
    
    # Check API connections
    print("\n2. API Connections:")
    
    # MFL API
    try:
        mfl = MFLAPI()
        transactions = mfl.get_transactions()
        print(f"   ✅ MFL API: {len(transactions)} transactions found")
    except Exception as e:
        print(f"   ❌ MFL API: {e}")
        return False
    
    # Odds API
    try:
        odds = OddsAPIClient()
        if odds.test_api_connection():
            print("   ✅ The Odds API: Connection successful")
        else:
            print("   ❌ The Odds API: Connection failed")
            return False
    except Exception as e:
        print(f"   ❌ The Odds API: {e}")
        return False
    
    # Discord API
    try:
        async def test_discord():
            notifier = DiscordNotifier()
            await notifier.send_notification("🧪 Configuration test - Discord working!")
            return True
        
        asyncio.run(test_discord())
        print("   ✅ Discord API: Test message sent")
    except Exception as e:
        print(f"   ❌ Discord API: {e}")
        return False
    
    # Basic system checks
    print("\n3. System Checks:")
    try:
        # Check if data directory exists and is writable
        import os
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        print("   ✅ Data directory: OK")
        
        # Check if we can write to data directory
        test_file = os.path.join(data_dir, "test_write.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("   ✅ Data directory writable: OK")
        
    except Exception as e:
        print(f"   ❌ System checks: {e}")
        return False
    
    print("\n🎉 Configuration validation completed successfully!")
    print("   Your MFL Transaction Monitor is ready to run!")
    return True

def main():
    success = validate_configuration()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
