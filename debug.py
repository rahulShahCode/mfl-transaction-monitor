#!/usr/bin/env python3
"""
Debug script for MFL Transaction Monitor
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.mfl_monitor.core.analyzer import TransactionAnalyzer
from src.mfl_monitor.core.scheduler import TransactionScheduler
from src.mfl_monitor.utils.config import Config
from src.mfl_monitor.apis.discord_bot import DiscordNotifier
from src.mfl_monitor.apis.mfl_api import MFLAPI
from src.mfl_monitor.apis.odds_api import OddsAPIClient

def debug_force_run():
    """Debug the force run with breakpoints"""
    print("🐛 Starting debug session...")
    
    # Set breakpoint here
    breakpoint()  # This will open pdb debugger
    
    print("✅ Configuration check...")
    if not Config.validate():
        print("❌ Configuration invalid")
        return
    
    print("✅ Creating analyzer...")
    analyzer = TransactionAnalyzer()
    
    print("✅ Running analysis...")
    # Set another breakpoint here
    breakpoint()
    
    import asyncio
    asyncio.run(analyzer.run_analysis())

def debug_mfl_api():
    """Debug MFL API calls"""
    print("🐛 Debugging MFL API...")
    
    breakpoint()  # Set breakpoint here
    
    mfl = MFLAPI()
    transactions = mfl.get_transactions()
    print(f"Found {len(transactions)} transactions")
    
    # Set another breakpoint to inspect transactions
    breakpoint()
    
    for i, transaction in enumerate(transactions[:5]):  # First 5 transactions
        print(f"Transaction {i}: {transaction}")

def debug_odds_api():
    """Debug Odds API calls"""
    print("🐛 Debugging Odds API...")
    
    breakpoint()  # Set breakpoint here
    
    odds = OddsAPIClient()
    game_times = odds.get_game_times_by_team()
    print(f"Found {len(game_times)} game times")
    
    # Set another breakpoint to inspect game times
    breakpoint()
    
    for team, time in list(game_times.items())[:5]:  # First 5 teams
        print(f"{team}: {time}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Debug MFL Transaction Monitor')
    parser.add_argument('--mode', choices=['force', 'mfl', 'odds'], default='force',
                       help='Debug mode to run')
    
    args = parser.parse_args()
    
    if args.mode == 'force':
        debug_force_run()
    elif args.mode == 'mfl':
        debug_mfl_api()
    elif args.mode == 'odds':
        debug_odds_api()
