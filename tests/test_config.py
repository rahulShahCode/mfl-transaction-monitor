"""
Tests for configuration management
"""

import unittest
from unittest.mock import patch
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mfl_monitor.utils.config import Config

class TestConfig(unittest.TestCase):
    """Test configuration validation and management"""
    
    def setUp(self):
        """Set up test environment"""
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Clean up test environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_validate_success(self):
        """Test successful configuration validation"""
        with patch.dict(os.environ, {
            'MFL_LEAGUE_ID': '12345',
            'ODDS_API_KEY': 'test_key',
            'DISCORD_BOT_TOKEN': 'test_token',
            'DISCORD_CHANNEL_ID': '123456789'
        }):
            self.assertTrue(Config.validate())
    
    def test_validate_missing_vars(self):
        """Test validation with missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(Config.validate())
    
    def test_validate_partial_vars(self):
        """Test validation with partial environment variables"""
        with patch.dict(os.environ, {
            'MFL_LEAGUE_ID': '12345',
            'ODDS_API_KEY': 'test_key'
        }, clear=True):
            self.assertFalse(Config.validate())

if __name__ == '__main__':
    unittest.main()
