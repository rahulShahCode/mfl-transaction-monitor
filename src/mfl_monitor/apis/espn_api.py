"""
ESPN API integration for NFL game times
"""

import requests
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from ..utils.config import Config

class ESPNAPIClient:
    """ESPN API client for NFL game times"""
    
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        
    def get_nfl_schedule(self, week: int = None) -> List[Dict]:
        """Get NFL schedule from ESPN API"""
        try:
            params = {}
            if week:
                params['week'] = week
                
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            print(f"✅ Retrieved {len(events)} NFL games from ESPN API")
            return events
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching NFL schedule from ESPN API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing ESPN API response: {e}")
            return []
    
    def get_game_times_by_team(self, week: int = None) -> Dict[str, datetime]:
        """Get game start times organized by team abbreviation"""
        events = self.get_nfl_schedule(week)
        team_game_times = {}
        
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
        
        for event in events:
            try:
                # Get game date and time
                date_str = event.get('date', '')
                if not date_str:
                    continue
                
                # Parse the date (format: "2025-09-06T00:00Z")
                game_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                
                # Get team names
                competitions = event.get('competitions', [])
                if not competitions:
                    continue
                
                competition = competitions[0]
                competitors = competition.get('competitors', [])
                if len(competitors) < 2:
                    continue
                
                home_team = competitors[0].get('team', {}).get('displayName', '')
                away_team = competitors[1].get('team', {}).get('displayName', '')
                
                if not home_team or not away_team:
                    continue
                
                # Map team names to abbreviations
                home_abbrev = team_mapping.get(home_team, home_team)
                away_abbrev = team_mapping.get(away_team, away_team)
                
                # Store game times for both teams
                team_game_times[home_abbrev] = game_time
                team_game_times[away_abbrev] = game_time
                
                print(f"📅 {home_team} vs {away_team} at {game_time}")
                
            except (ValueError, KeyError) as e:
                print(f"⚠️  Error processing game {event}: {e}")
                continue
        
        return team_game_times
    
    def get_current_week_games(self) -> Dict[str, datetime]:
        """Get games for the current week (Thursday to Monday)"""
        # Get current week number
        current_week = self.get_current_week()
        
        # Get all games for current week
        all_games = self.get_game_times_by_team(current_week)
        
        # Filter to only include Thursday to Monday games
        now = datetime.now(timezone.utc)
        
        # Find the most recent Thursday
        if now.weekday() > 3 or (now.weekday() == 3 and now.hour >= 20):
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
        
        # Filter games to only include this week's games
        filtered_games = {}
        for team, game_time in all_games.items():
            if this_thursday <= game_time <= next_monday:
                filtered_games[team] = game_time
        
        print(f"📅 Found {len(filtered_games)} teams playing this week (Thursday to Monday)")
        return filtered_games
    
    def get_current_week(self) -> int:
        """Get current NFL week number"""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            week_info = data.get('week', {})
            return week_info.get('number', 1)
            
        except Exception as e:
            print(f"⚠️  Error getting current week: {e}")
            return 1
    
    def test_api_connection(self) -> bool:
        """Test ESPN API connection"""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            print(f"✅ ESPN API connection successful - found {len(events)} games")
            return True
            
        except Exception as e:
            print(f"❌ ESPN API connection failed: {e}")
            return False
