"""
Configuration management for MFL Transaction Monitor
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for MFL Transaction Monitor"""
    
    # MFL Configuration
    MFL_LEAGUE_ID = os.getenv('MFL_LEAGUE_ID')
    MFL_API_KEY = os.getenv('MFL_API_KEY')
    MFL_YEAR = os.getenv('MFL_YEAR', '2025')
    MFL_API_URL = f"https://www.myfantasyleague.com/{MFL_YEAR}/export"
    
    # The Odds API Configuration
    ODDS_API_KEY = os.getenv('ODDS_API_KEY')
    
    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
    
    # Scheduling Configuration
    SCHEDULE_START_DAY = 'thursday'
    SCHEDULE_START_TIME = '20:00'
    SCHEDULE_END_DAY = 'monday'
    SCHEDULE_END_TIME = '22:00'
    SKIP_START_TIME = '00:00'
    SKIP_END_TIME = '09:00'
    
    # Data persistence
    DATA_FILE = 'data/transaction_data.json'
    CACHE_FILE = 'data/game_times_cache.json'
    QUOTA_FILE = 'data/odds_api_quota.json'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            'MFL_LEAGUE_ID',
            'MFL_API_KEY',
            'ODDS_API_KEY', 
            'DISCORD_BOT_TOKEN',
            'DISCORD_CHANNEL_ID'
        ]
        
        missing = []
        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)
        
        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            return False
        
        print("✅ All required configuration variables are set")
        return True
