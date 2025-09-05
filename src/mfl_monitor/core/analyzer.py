"""
MFL transaction monitor - checks for players picked up after their games start
"""

import json
import os
import re
import asyncio
import pytz
from datetime import datetime, timezone
from typing import List, Dict, Optional
from ..utils.config import Config
from ..apis.mfl_api import MFLAPI
from ..apis.discord_bot import DiscordNotifier
from ..utils.cache import GameTimeCache

class TransactionAnalyzer:
    """Checks if anyone picked up players after their games started"""
    
    def __init__(self):
        self.mfl_api = MFLAPI()
        self.discord_notifier = DiscordNotifier()
        self.cache = GameTimeCache()
        self.data_file = Config.DATA_FILE
        self.last_run_data = self.load_last_run_data()
        
    def load_last_run_data(self) -> Dict:
        """Load when we last checked transactions"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading last run data: {e}")
                return {}
        return {}
    
    def save_last_run_data(self, data: Dict):
        """Save when we last ran"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except IOError as e:
            print(f"Error saving last run data: {e}")
    
    def get_game_start_times(self) -> Dict[str, datetime]:
        """Get when each team's games start"""
        game_times = self.cache.get_game_times()
        return game_times
    
    def is_player_pickup_after_game_start(self, transaction: Dict, game_times: Dict[str, datetime]) -> bool:
        """See if someone picked up a player after their game already started"""
        try:
            transaction_type = transaction.get('type', '')
            if transaction_type not in ['FREE_AGENT', 'BBID_WAIVER', 'BBID_AUTO_PROCESS_WAIVERS']:
                return False
            
            timestamp_str = transaction.get('timestamp', '')
            if not timestamp_str:
                return False
            
            try:
                timestamp_int = int(timestamp_str)
                transaction_time = datetime.fromtimestamp(timestamp_int, tz=timezone.utc)
            except ValueError:
                print(f"Invalid timestamp format: {timestamp_str}")
                return False
            
            transaction_data = transaction.get('transaction', '')
            if not transaction_data or ',' not in transaction_data or '|' not in transaction_data:
                return False
            
            added_players_str = transaction_data.split('|')[0].rstrip(',')
            if not added_players_str:
                return False
            
            player_id = added_players_str.split(',')[0]
            if not player_id:
                return False
            
            players = self.mfl_api.get_players()
            if player_id not in players:
                print(f"Player {player_id} not found in players data")
                return False
            
            player_team = players[player_id].get('team', '')
            player_name = players[player_id].get('name', 'Unknown Player')
            if not player_team or player_team not in game_times:
                print(f"Player {player_name} ({player_id}) team {player_team} not found in game times")
                return False
            
            game_start_time = game_times[player_team]
            is_after = transaction_time > game_start_time
            
            if is_after:
                print(f"VIOLATION: Player {player_name} ({player_id}) picked up at {transaction_time} after game start at {game_start_time}")
            
            return is_after
            
        except (ValueError, KeyError) as e:
            print(f"Error checking transaction timing: {e}")
            return False
    
    def format_transaction_message(self, transaction: Dict, players: Dict, franchises: Dict, game_start_time: datetime = None) -> str:
        """Create the Discord message for violations"""
        try:
            transaction_data = transaction.get('transaction', '')
            if ',' in transaction_data and '|' in transaction_data:
                added_players_str = transaction_data.split('|')[0].rstrip(',')
                player_id = added_players_str.split(',')[0] if added_players_str else ''
            else:
                player_id = ''
            
            franchise_id = transaction.get('franchise', '')
            timestamp = transaction.get('timestamp', '')
            
            # Get player info
            player_name = "Unknown Player"
            player_position = "Unknown"
            player_team_abbrev = "Unknown"
            
            if player_id and player_id in players:
                player_data = players[player_id]
                # Format name as "First Last" instead of "Last, First"
                full_name = player_data.get('name', 'Unknown Player')
                if ', ' in full_name:
                    last_name, first_name = full_name.split(', ', 1)
                    player_name = f"{first_name} {last_name}"
                else:
                    player_name = full_name
                
                player_position = player_data.get('position', 'Unknown')
                player_team_abbrev = player_data.get('team', 'Unknown')
            
            # Get franchise info
            franchise_name = "Unknown Team"
            owner_name = "Unknown Owner"
            
            if franchise_id in franchises:
                franchise_data = franchises[franchise_id]
                franchise_name = franchise_data.get('name', 'Unknown Team')
                owner_name = franchise_data.get('owner_name', 'Unknown Owner')
            
            # Convert pickup time to New York timezone
            try:
                timestamp_int = int(timestamp)
                dt_utc = datetime.fromtimestamp(timestamp_int, tz=timezone.utc)
                # Convert to New York time
                ny_tz = pytz.timezone('America/New_York')
                dt_ny = dt_utc.astimezone(ny_tz)
                time_str = dt_ny.strftime("%m/%d %I:%M %p %Z")
                # Clean up the time format
                pickup_time = re.sub(r'0(\d):', r'\1:', time_str)  # Remove leading zero from hour
                pickup_time = re.sub(r'0(\d)/', r'\1/', pickup_time)  # Remove leading zero from month
                pickup_time = re.sub(r'/(\d{2})', lambda m: f'/{int(m.group(1))}', pickup_time)  # Remove leading zero from day
            except ValueError:
                pickup_time = timestamp
            
            # Format game start time if provided
            game_time_str = ""
            if game_start_time:
                try:
                    # Convert game start time to New York timezone
                    if game_start_time.tzinfo is None:
                        game_start_time = game_start_time.replace(tzinfo=timezone.utc)
                    game_ny = game_start_time.astimezone(ny_tz)
                    game_time_formatted = re.sub(r'0(\d):', r'\1:', game_ny.strftime('%I:%M %p %Z'))
                    game_date_formatted = game_ny.strftime('%m/%d')
                    # Clean up the date format
                    game_date_formatted = re.sub(r'0(\d)/', r'\1/', game_date_formatted)  # Remove leading zero from month
                    game_date_formatted = re.sub(r'/(\d{2})', lambda m: f'/{int(m.group(1))}', game_date_formatted)  # Remove leading zero from day
                    game_time_str = f" | Game started: {game_date_formatted} {game_time_formatted}"
                except Exception as e:
                    print(f"Error formatting game time: {e}")
            
            message = (
                f"🚨 **{player_name} ({player_position}, {player_team_abbrev})** picked up by **{franchise_name} ({owner_name})**\n"
                f"⏰ {pickup_time}{game_time_str}"
            )
            
            return message
            
        except Exception as e:
            print(f"Error formatting transaction message: {e}")
            return f"Transaction alert: {transaction}"
    
    def analyze_transactions(self) -> List[str]:
        """Check all transactions and find violations"""
        print("Starting transaction analysis...")
        
        current_time = datetime.now(timezone.utc)
        
        last_run_time = self.last_run_data.get('last_run_time')
        if last_run_time:
            last_run_time = datetime.fromisoformat(last_run_time)
        else:
            last_run_time = current_time - timedelta(hours=24)
        
        print(f"Checking transactions since: {last_run_time}")
        
        transactions = self.mfl_api.get_transactions(last_run_time)
        players = self.mfl_api.get_players()
        franchises = self.mfl_api.get_franchises()
        game_times = self.get_game_start_times()
        
        print(f"Found {len(transactions)} transactions to analyze")
        
        # Only check transactions that happened after our last run
        filtered_transactions = []
        for transaction in transactions:
            try:
                timestamp_str = transaction.get('timestamp', '')
                if timestamp_str:
                    timestamp_int = int(timestamp_str)
                    transaction_time = datetime.fromtimestamp(timestamp_int, tz=timezone.utc)
                    if transaction_time > last_run_time:
                        filtered_transactions.append(transaction)
            except (ValueError, TypeError):
                # Skip bad timestamps
                continue
        
        print(f"Processing {len(filtered_transactions)} transactions after last run time")
        
        violation_messages = []
        
        for transaction in filtered_transactions:
            if self.is_player_pickup_after_game_start(transaction, game_times):
                # Get the game start time for this player's team
                game_start_time = None
                try:
                    transaction_data = transaction.get('transaction', '')
                    if ',' in transaction_data and '|' in transaction_data:
                        added_players_str = transaction_data.split('|')[0].rstrip(',')
                        player_id = added_players_str.split(',')[0] if added_players_str else ''
                        if player_id and player_id in players:
                            player_team = players[player_id].get('team', '')
                            if player_team in game_times:
                                game_start_time = game_times[player_team]
                except Exception as e:
                    print(f"Error getting game start time: {e}")
                
                message = self.format_transaction_message(transaction, players, franchises, game_start_time)
                violation_messages.append(message)
                print(f"Found violation: {message}")
        
        self.last_run_data['last_run_time'] = current_time.isoformat()
        self.save_last_run_data(self.last_run_data)
        
        return violation_messages
    
    async def run_analysis(self):
        """Run the check and send Discord alerts"""
        try:
            violation_messages = self.analyze_transactions()
            
            if violation_messages:
                print(f"Found {len(violation_messages)} violations")
                for message in violation_messages:
                    await self.discord_notifier.send_notification(message)
                    await asyncio.sleep(1)
            else:
                print("No violations found")
                
        except Exception as e:
            print(f"Error during analysis: {e}")
            await self.discord_notifier.send_notification(f"❌ Error in transaction analysis: {str(e)}")
