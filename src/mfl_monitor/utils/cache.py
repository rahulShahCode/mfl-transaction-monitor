"""
Game time caching to reduce API calls
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
from .config import Config
from ..apis.odds_api import OddsAPIClient

class GameTimeCache:
    """Caches NFL game times to reduce API calls"""
    
    def __init__(self, cache_file: str = None):
        self.cache_file = cache_file or Config.CACHE_FILE
        self.cache_duration_hours = 6
        self.cache_data = self.load_cache()
    
    def load_cache(self) -> Dict:
        """Load cached game times"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            'game_times': {},
            'cached_at': None,
            'week_range': None
        }
    
    def save_cache(self, game_times: Dict, week_range: str):
        """Save game times to cache"""
        self.cache_data = {
            'game_times': {k: v.isoformat() for k, v in game_times.items()},
            'cached_at': datetime.now().isoformat(),
            'week_range': week_range
        }
        
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save game cache: {e}")
    
    def is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.cache_data.get('cached_at'):
            return False
        
        try:
            cached_at = datetime.fromisoformat(self.cache_data['cached_at'])
            if cached_at.tzinfo is None:
                cached_at = cached_at.replace(tzinfo=timezone.utc)
            cache_age = datetime.now(timezone.utc) - cached_at
            return cache_age.total_seconds() < (self.cache_duration_hours * 3600)
        except ValueError:
            return False
    
    def get_current_week_range(self) -> str:
        """Get current week range (Thursday to Monday)"""
        now = datetime.now(timezone.utc)
        
        days_until_thursday = (3 - now.weekday()) % 7
        if days_until_thursday == 0 and now.weekday() != 3:
            days_until_thursday = 7
        elif now.weekday() > 3:
            days_until_thursday = (3 - now.weekday()) % 7 + 7
        
        this_thursday = now + timedelta(days=days_until_thursday)
        this_thursday = this_thursday.replace(hour=0, minute=0, second=0, microsecond=0)
        next_monday = this_thursday + timedelta(days=5)
        
        return f"{this_thursday.strftime('%Y-%m-%d')}_to_{next_monday.strftime('%Y-%m-%d')}"
    
    def get_game_times(self) -> Dict[str, datetime]:
        """Get game times, using cache if valid"""
        current_week = self.get_current_week_range()
        
        if (self.is_cache_valid() and 
            self.cache_data.get('week_range') == current_week and
            self.cache_data.get('game_times')):
            
            print("📅 Using cached game times")
            game_times = {}
            for team, time_str in self.cache_data['game_times'].items():
                try:
                    game_times[team] = datetime.fromisoformat(time_str)
                except ValueError:
                    continue
            return game_times
        
        print("📅 Cache invalid or different week, fetching new game times")
        
        # Try ESPN API first (more reliable for current games)
        try:
            from ..apis.espn_api import ESPNAPIClient
            espn_client = ESPNAPIClient()
            game_times = espn_client.get_current_week_games()
            
            if game_times:
                print("📅 Using ESPN API for game times")
            else:
                raise Exception("No games found from ESPN API")
                
        except Exception as e:
            print(f"⚠️  ESPN API failed: {e}, falling back to Odds API")
            # Fallback to Odds API
            odds_client = OddsAPIClient()
            game_times = odds_client.get_game_times_by_team(days_back=7, days_ahead=5)
        
        if game_times:
            self.save_cache(game_times, current_week)
            print(f"📅 Cached {len(game_times)} game times for {current_week}")
        
        return game_times
    
    def clear_cache(self):
        """Clear the cache"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.cache_data = {'game_times': {}, 'cached_at': None, 'week_range': None}
        print("📅 Game time cache cleared")
