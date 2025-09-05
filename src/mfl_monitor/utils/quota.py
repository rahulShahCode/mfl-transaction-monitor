"""
API quota management for The Odds API
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict
from .config import Config

class QuotaManager:
    """Manages API quota usage and tracking"""
    
    def __init__(self):
        self.quota_file = Config.QUOTA_FILE
        self.quota_data = self.load_quota_data()
    
    def load_quota_data(self) -> Dict:
        """Load quota usage data from file"""
        if os.path.exists(self.quota_file):
            try:
                with open(self.quota_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            'requests_used': 0,
            'requests_remaining': 500,
            'last_reset': None,
            'daily_usage': {}
        }
    
    def save_quota_data(self):
        """Save quota usage data to file"""
        try:
            os.makedirs(os.path.dirname(self.quota_file), exist_ok=True)
            with open(self.quota_file, 'w') as f:
                json.dump(self.quota_data, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Could not save quota data: {e}")
    
    def update_quota_usage(self, response_headers: Dict):
        """Update quota usage based on response headers"""
        try:
            requests_used = int(response_headers.get('x-requests-used', 0))
            requests_remaining = int(response_headers.get('x-requests-remaining', 0))
            
            self.quota_data['requests_used'] = requests_used
            self.quota_data['requests_remaining'] = requests_remaining
            self.quota_data['last_reset'] = datetime.now().isoformat()
            
            today = datetime.now().strftime('%Y-%m-%d')
            if today not in self.quota_data['daily_usage']:
                self.quota_data['daily_usage'][today] = 0
            self.quota_data['daily_usage'][today] += 1
            
            self.save_quota_data()
            
            print(f"📊 Quota: {requests_used} used, {requests_remaining} remaining")
            
        except (ValueError, KeyError) as e:
            print(f"Warning: Could not parse quota headers: {e}")
    
    def check_quota_status(self) -> bool:
        """Check if we have quota remaining"""
        remaining = self.quota_data.get('requests_remaining', 0)
        if remaining <= 0:
            print("⚠️  No API quota remaining!")
            return False
        elif remaining < 10:
            print(f"⚠️  Low API quota: {remaining} requests remaining")
        return True
    
    def get_quota_status(self) -> Dict:
        """Get current quota status"""
        return {
            'requests_used': self.quota_data.get('requests_used', 0),
            'requests_remaining': self.quota_data.get('requests_remaining', 0),
            'last_reset': self.quota_data.get('last_reset'),
            'daily_usage': self.quota_data.get('daily_usage', {})
        }
