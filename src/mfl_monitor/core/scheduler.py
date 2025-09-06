"""
Transaction scheduling and time management
"""

import asyncio
from datetime import datetime, time
import pytz
from ..utils.config import Config
from .analyzer import TransactionAnalyzer

class TransactionScheduler:
    """Schedules and manages transaction monitoring"""
    
    def __init__(self):
        self.analyzer = TransactionAnalyzer()
        self.timezone = pytz.timezone('America/New_York')
        
    def is_within_active_hours(self) -> bool:
        """Check if current time is within the active monitoring hours"""
        now = datetime.now(self.timezone)
        current_time = now.time()
        current_weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        weekday_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        start_day = weekday_map.get(Config.SCHEDULE_START_DAY.lower(), 3)
        end_day = weekday_map.get(Config.SCHEDULE_END_DAY.lower(), 0)
        
        start_time = datetime.strptime(Config.SCHEDULE_START_TIME, '%H:%M').time()
        end_time = datetime.strptime(Config.SCHEDULE_END_TIME, '%H:%M').time()
        skip_start = datetime.strptime(Config.SKIP_START_TIME, '%H:%M').time()
        skip_end = datetime.strptime(Config.SKIP_END_TIME, '%H:%M').time()
        
        # Check if we're in the skip period (12AM to 9AM)
        if skip_start <= current_time <= skip_end:
            return False
        
        # Check if we're in the active period
        # Thursday (3) 8PM to Monday (0) 10PM
        is_active = False
        
        if current_weekday == start_day and current_time >= start_time:
            is_active = True
        elif current_weekday == end_day and current_time <= end_time:
            is_active = True
        elif start_day < current_weekday < end_day:
            is_active = True
        elif current_weekday == 4 or current_weekday == 5 or current_weekday == 6:  # Fri, Sat, Sun
            is_active = True
        
        return is_active
    
    async def run_check(self, force=False):
        """Run a single transaction check"""
        if force or self.is_within_active_hours():
            print(f"Running transaction check at {datetime.now()}")
            await self.analyzer.run_analysis()
        else:
            print(f"Skipping check at {datetime.now()} - outside active hours")
    
    def run_once(self):
        """Run a single check immediately (useful for testing)"""
        print("Running single transaction check...")
        asyncio.run(self.run_check())
