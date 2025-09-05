# 🏈 MFL Transaction Monitor

A professional Python package that monitors MyFantasyLeague transactions and sends Discord notifications when players are picked up after their game has started.

## ✨ Features

- **Real-time Monitoring**: Uses The Odds API for accurate NFL game times
- **Smart Scheduling**: Runs Thursday 8PM to Monday 10PM, skips 12AM-9AM
- **Discord Integration**: Sends formatted notifications with player details
- **Efficient Caching**: Reduces API calls with 6-hour game time caching
- **GitHub Actions**: Runs automatically in the cloud
- **Quota Management**: Tracks API usage and prevents overages
- **Professional Structure**: Clean, modular, and maintainable code

## 🚀 Quick Start

### Option 1: GitHub Actions (Recommended)
1. Fork this repository
2. Set up GitHub Secrets (see [Setup Guide](SETUP.md))
3. Enable GitHub Actions
4. Done! Runs automatically every hour

### Option 2: Local Machine
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables (see [Environment Setup](#environment-setup))
3. Run: `python main.py`

## 📋 Environment Setup

Create a `.env` file with your credentials:

```bash
# MyFantasyLeague
MFL_LEAGUE_ID=your_league_id_here
MFL_API_KEY=your_mfl_api_key_here
MFL_YEAR=2025

# The Odds API
ODDS_API_KEY=your_odds_api_key_here

# Discord Bot
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here
```

## 🛠️ Usage

### Commands
```bash
# Test configuration
python main.py --test

# Run once (respects time restrictions)
python main.py --once

# Force run (ignores time restrictions)
python main.py --force

# Run continuously
python main.py
```

### Utility Scripts
```bash
# Check API quota usage
python scripts/check_quota.py

# Set last run time
python scripts/set_last_run.py --hours 24
```

## 📁 Project Structure

```
mfl-transaction-monitor/
├── src/mfl_monitor/           # Main package
│   ├── apis/                  # API integrations
│   ├── core/                  # Core functionality
│   └── utils/                 # Utilities
├── scripts/                   # Utility scripts
├── data/                      # Runtime data files
├── .github/workflows/         # GitHub Actions
└── main.py                    # Main entry point
```

See [Project Structure](PROJECT_STRUCTURE.md) for detailed organization.

## 🔧 Configuration

### Scheduling
- **Active Period**: Thursday 8PM to Monday 10PM EST
- **Skip Period**: 12AM to 9AM daily
- **Frequency**: Every hour during active periods

### API Limits
- **The Odds API**: 500 requests/month (free tier)
- **Caching**: 6 hours for game times
- **Efficiency**: ~5 requests per day with caching

## 📊 How It Works

1. **Fetches Game Times**: Gets current week's NFL games from The Odds API
2. **Caches Data**: Stores game times for 6 hours to reduce API calls
3. **Monitors Transactions**: Checks MFL for new player pickups
4. **Detects Violations**: Identifies pickups after game start times
5. **Sends Alerts**: Notifies Discord channel with violation details

## 🚨 Discord Notifications

When a violation is detected, sends formatted message:
```
🚨 Transaction Alert
Player: Josh Allen
Team: Buffalo Bills
Owner: John Smith
Action: Free Agent
Time: 2025-09-21 2:30 PM
```

## 📈 Monitoring

### GitHub Actions
- View logs in Actions tab
- Manual triggers available
- Automatic error notifications

### Local Monitoring
- Check `data/transaction_data.json` for last run time
- Monitor `data/odds_api_quota.json` for API usage
- View console output for real-time status

## 🛠️ Troubleshooting

### Common Issues
1. **"Missing environment variables"** - Check your `.env` file
2. **"API connection failed"** - Verify API keys are correct
3. **"No violations found"** - Normal if no pickups after game start
4. **"Quota exceeded"** - Wait for reset or upgrade plan

### Testing
```bash
# Test all connections
python main.py --test

# Check quota status
python scripts/check_quota.py

# Force run with debug info
python main.py --force
```

## 📚 Documentation

- [Setup Guide](SETUP.md) - Complete setup instructions
- [Project Structure](PROJECT_STRUCTURE.md) - Code organization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Verify all environment variables
4. Test with `--force` flag

---

**Ready to catch those sneaky post-game pickups!** 🏈⚡