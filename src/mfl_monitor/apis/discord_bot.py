"""
Discord bot integration for notifications
"""

import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from ..utils.config import Config

class DiscordNotifier:
    """Handles Discord notifications"""
    
    def __init__(self):
        self.bot_token = Config.DISCORD_BOT_TOKEN
        self.channel_id = int(Config.DISCORD_CHANNEL_ID)
        self.bot = None
        self.channel = None
        
    async def initialize(self):
        """Initialize the Discord bot and get the channel"""
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user} has connected to Discord!')
            self.channel = self.bot.get_channel(self.channel_id)
            if self.channel:
                print(f'Connected to channel: {self.channel.name}')
            else:
                print(f'Could not find channel with ID: {self.channel_id}')
        
        await self.bot.start(self.bot_token)
    
    async def send_notification(self, message: str):
        """Send a notification message to the Discord channel"""
        try:
            # Create a new bot instance for each message
            intents = discord.Intents.default()
            intents.message_content = True
            
            bot = commands.Bot(command_prefix='!', intents=intents)
            
            @bot.event
            async def on_ready():
                channel = bot.get_channel(self.channel_id)
                if channel:
                    await channel.send(message)
                    print(f"✅ Sent Discord notification: {message}")
                else:
                    print(f"❌ Could not find Discord channel with ID: {self.channel_id}")
                await bot.close()
            
            await bot.start(self.bot_token)
            return True
            
        except Exception as e:
            print(f"❌ Error sending Discord notification: {e}")
            return False
    
    async def send_transaction_alert(self, transaction_data: dict):
        """Send a formatted transaction alert to Discord"""
        player_name = transaction_data.get('player_name', 'Unknown Player')
        team_name = transaction_data.get('team_name', 'Unknown Team')
        owner_name = transaction_data.get('owner_name', 'Unknown Owner')
        transaction_type = transaction_data.get('type', 'pickup')
        timestamp = transaction_data.get('timestamp', 'Unknown Time')
        
        embed = discord.Embed(
            title="🚨 Transaction Alert",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Player", value=player_name, inline=True)
        embed.add_field(name="Team", value=team_name, inline=True)
        embed.add_field(name="Owner", value=owner_name, inline=True)
        embed.add_field(name="Action", value=transaction_type.title(), inline=True)
        embed.add_field(name="Time", value=timestamp, inline=True)
        
        embed.set_footer(text="MyFantasyLeague Transaction Monitor")
        
        if not self.channel:
            print("Discord channel not available")
            return False
            
        try:
            await self.channel.send(embed=embed)
            print(f"Sent Discord transaction alert for {player_name}")
            return True
        except Exception as e:
            print(f"Error sending Discord transaction alert: {e}")
            return False
    
    async def close(self):
        """Close the Discord bot connection"""
        if self.bot:
            await self.bot.close()

# Standalone function for sending notifications without running a full bot
async def send_simple_notification(message: str):
    """Send a simple text notification to Discord"""
    notifier = DiscordNotifier()
    try:
        intents = discord.Intents.default()
        bot = commands.Bot(command_prefix='!', intents=intents)
        
        @bot.event
        async def on_ready():
            channel = bot.get_channel(int(Config.DISCORD_CHANNEL_ID))
            if channel:
                await channel.send(message)
                print(f"Sent notification: {message}")
            else:
                print(f"Could not find channel with ID: {Config.DISCORD_CHANNEL_ID}")
            await bot.close()
        
        await bot.start(Config.DISCORD_BOT_TOKEN)
        
    except Exception as e:
        print(f"Error sending Discord notification: {e}")
