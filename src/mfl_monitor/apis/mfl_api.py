"""
MFL API calls
"""

import requests
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional
from ..utils.config import Config

class MFLAPI:
    """Gets data from MFL"""
    
    def __init__(self):
        self.league_id = Config.MFL_LEAGUE_ID
        self.api_key = Config.MFL_API_KEY
        self.year = Config.MFL_YEAR
        self.base_url = Config.MFL_API_URL
        
    def get_transactions(self, since: Optional[datetime] = None) -> List[Dict]:
        """Get transactions from MFL"""
        try:
            params = {
                'TYPE': 'transactions',
                'L': self.league_id,
                'APIKEY': self.api_key,
                'JSON': 1
            }
            
            if since:
                # Only get transactions after our last check
                timestamp = int(since.timestamp())
                params['SINCE'] = timestamp
                params['DAYS'] = 7
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'transactions' in data and 'transaction' in data['transactions']:
                transactions = data['transactions']['transaction']
                if isinstance(transactions, dict):
                    transactions = [transactions]
                return transactions
            else:
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transactions from MFL: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing MFL response: {e}")
            return []
    
    def get_players(self) -> Dict[str, Dict]:
        """Get player info from MFL"""
        try:
            params = {
                'TYPE': 'players',
                'L': self.league_id,
                'APIKEY': self.api_key,
                'JSON': 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'players' in data and 'player' in data['players']:
                players = data['players']['player']
                player_dict = {}
                if isinstance(players, list):
                    for player in players:
                        player_dict[player['id']] = player
                else:
                    player_dict[players['id']] = players
                return player_dict
            else:
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching players from MFL: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing MFL players response: {e}")
            return {}
    
    def get_franchises(self) -> Dict[str, Dict]:
        """Get team info from MFL"""
        try:
            params = {
                'TYPE': 'league',
                'L': self.league_id,
                'APIKEY': self.api_key,
                'JSON': 1,
                'FRANCHISES': 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'league' in data and 'franchises' in data['league'] and 'franchise' in data['league']['franchises']:
                franchises = data['league']['franchises']['franchise']
                franchise_dict = {}
                if isinstance(franchises, list):
                    for franchise in franchises:
                        franchise_dict[franchise['id']] = franchise
                else:
                    franchise_dict[franchises['id']] = franchises
                return franchise_dict
            else:
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching franchises from MFL: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing MFL franchises response: {e}")
            return {}
