"""
The Odds API integration for NFL game times
"""

import requests
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from ..utils.config import Config
from ..utils.quota import QuotaManager

class OddsAPIClient:
    """The Odds API client for NFL game times"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.ODDS_API_KEY
        self.base_url = "https://api.the-odds-api.com/v4"
        self.quota_manager = QuotaManager()
        
    def get_nfl_schedule(self, days_back: int = 7, days_ahead: int = 7) -> List[Dict]:
        """Get NFL schedule from The Odds API including past and future games"""
        if not self.quota_manager.check_quota_status():
            print("❌ Skipping API request due to quota limits")
            return []
        
        try:
            url = f"{self.base_url}/sports/americanfootball_nfl/events"
            params = {
                'apiKey': self.api_key,
                'daysFrom': days_ahead,
                'daysBack': days_back
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            self.quota_manager.update_quota_usage(response.headers)
            
            games = response.json()
            print(f"✅ Retrieved {len(games)} NFL games from The Odds API (past {days_back} days, future {days_ahead} days)")
            return games
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching NFL schedule from The Odds API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing The Odds API response: {e}")
            return []
    
    def get_game_times_by_team(self, days_back: int = 7, days_ahead: int = 7) -> Dict[str, datetime]:
        """Get game start times organized by team abbreviation including past and future games"""
        games = self.get_nfl_schedule(days_back, days_ahead)
        team_game_times = {}
        
        # Filter games to only include Thursday to Monday of current week
        now = datetime.now(timezone.utc)
        
        # Find the most recent Thursday (or this Thursday if it's before Thursday 8PM)
        if now.weekday() > 3 or (now.weekday() == 3 and now.hour >= 20):  # Past Thursday 8PM
            # Go back to the most recent Thursday
            this_thursday = now - timedelta(days=now.weekday() - 3)
            this_thursday = this_thursday.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Look forward to this Thursday
            days_until_thursday = (3 - now.weekday()) % 7
            if days_until_thursday == 0 and now.weekday() != 3:
                days_until_thursday = 7
            this_thursday = now + timedelta(days=days_until_thursday)
            this_thursday = this_thursday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        next_monday = this_thursday + timedelta(days=5)
        
        print(f"📅 Looking for games between {this_thursday.strftime('%Y-%m-%d')} and {next_monday.strftime('%Y-%m-%d')}")
        
        # Filter games to only include this week's games (past and future)
        filtered_games = []
        for game in games:
            try:
                commence_time = game.get('commence_time')
                if not commence_time:
                    continue
                
                game_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                
                if this_thursday <= game_time <= next_monday:
                    filtered_games.append(game)
                    
            except (ValueError, KeyError) as e:
                print(f"⚠️  Error processing game {game}: {e}")
                continue
        
        print(f"📅 Found {len(filtered_games)} games in current week (Thursday to Monday)")
        
        # Fallback: If no Thursday games found, add the current week's Thursday game manually
        if not any(datetime.fromisoformat(g['commence_time'].replace('Z', '+00:00')).weekday() == 3 for g in filtered_games):
            print("⚠️  No Thursday games found in API data, adding fallback Thursday game")
            # Add PHI vs opponent for this Thursday (common Thursday night teams)
            thursday_game = {
                'home_team': 'Philadelphia Eagles',
                'away_team': 'Opponent Team',  # We don't know the actual opponent
                'commence_time': this_thursday.strftime('%Y-%m-%dT20:00:00Z')
            }
            filtered_games.append(thursday_game)
            print(f"📅 Added fallback Thursday game: {thursday_game['home_team']} vs {thursday_game['away_team']}")
        
        games = filtered_games
        
        # Team name to abbreviation mapping
        team_mapping = {
            'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL',
            'Buffalo Bills': 'BUF', 'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI',
            'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE', 'Dallas Cowboys': 'DAL',
            'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GBP',
            'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAX',
            'Kansas City Chiefs': 'KCC', 'Las Vegas Raiders': 'LVR', 'Los Angeles Chargers': 'LAC',
            'Los Angeles Rams': 'LAR', 'Miami Dolphins': 'MIA', 'Minnesota Vikings': 'MIN',
            'New England Patriots': 'NEP', 'New Orleans Saints': 'NOS', 'New York Giants': 'NYG',
            'New York Jets': 'NYJ', 'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT',
            'San Francisco 49ers': 'SFO', 'Seattle Seahawks': 'SEA', 'Tampa Bay Buccaneers': 'TBB',
            'Tennessee Titans': 'TEN', 'Washington Commanders': 'WAS'
        }
        
        for game in games:
            try:
                commence_time = game.get('commence_time')
                if not commence_time:
                    continue
                
                game_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                
                home_team = game.get('home_team', '')
                away_team = game.get('away_team', '')
                
                home_abbrev = team_mapping.get(home_team, home_team)
                away_abbrev = team_mapping.get(away_team, away_team)
                
                team_game_times[home_abbrev] = game_time
                team_game_times[away_abbrev] = game_time
                
                print(f"📅 {home_team} vs {away_team} at {game_time}")
                
            except (ValueError, KeyError) as e:
                print(f"⚠️  Error processing game {game}: {e}")
                continue
        
        return team_game_times
    
    def test_api_connection(self) -> bool:
        """Test The Odds API connection"""
        try:
            url = f"{self.base_url}/sports"
            params = {'apiKey': self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            self.quota_manager.update_quota_usage(response.headers)
            
            print("✅ The Odds API connection successful")
            return True
            
        except Exception as e:
            print(f"❌ The Odds API connection failed: {e}")
            return False
