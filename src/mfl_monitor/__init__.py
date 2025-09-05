"""
MFL Transaction Monitor

A Python package for monitoring MyFantasyLeague transactions and detecting
violations when players are picked up after their game has started.
"""

__version__ = "1.0.0"
__author__ = "MFL Transaction Monitor"
__description__ = "Monitor MFL transactions and detect post-game pickups"

from .core.analyzer import TransactionAnalyzer
from .core.scheduler import TransactionScheduler
from .apis.mfl_api import MFLAPI
from .apis.odds_api import OddsAPIClient
from .apis.discord_bot import DiscordNotifier

__all__ = [
    "TransactionAnalyzer",
    "TransactionScheduler", 
    "MFLAPI",
    "OddsAPIClient",
    "DiscordNotifier"
]
