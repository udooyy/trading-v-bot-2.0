# TradingView AI Trading Bot 2.0

A sophisticated AI-powered trading bot designed to integrate seamlessly with TradingView signals and execute automated trading strategies across multiple exchanges.

## Features

### 🤖 AI-Powered Analysis
- **Technical Indicator Analysis**: RSI, MACD, Bollinger Bands, and 20+ indicators
- **Pattern Recognition**: Chart pattern detection using machine learning
- **Sentiment Analysis**: News and social media sentiment integration
- **Price Prediction**: LSTM neural networks for trend forecasting

### 📈 TradingView Integration
- **Webhook Support**: Receive real-time signals from TradingView alerts
- **Strategy Automation**: Execute trades based on Pine Script signals
- **Multi-timeframe Analysis**: Support for different timeframe strategies
- **Custom Signal Processing**: Parse and validate TradingView alert messages

### 🏦 Exchange Support
- **Multi-Exchange**: Binance, Coinbase Pro, Kraken, and more via CCXT
- **Spot & Futures**: Support for both spot and futures trading
- **Portfolio Management**: Cross-exchange portfolio tracking
- **Risk Management**: Advanced position sizing and risk controls

### 🛡️ Risk Management
- **Position Sizing**: Kelly Criterion and fixed percentage methods
- **Stop Loss/Take Profit**: Automatic order management
- **Drawdown Protection**: Maximum daily/weekly loss limits
- **Portfolio Diversification**: Automatic risk distribution

### 📊 Real-time Monitoring
- **Web Dashboard**: Live trading performance and metrics
- **Real-time Alerts**: Email, SMS, and webhook notifications
- **Performance Analytics**: Detailed profit/loss analysis
- **Trade Journal**: Complete trading history with analytics

### 🔧 Advanced Features
- **Backtesting Engine**: Historical strategy validation
- **Paper Trading**: Risk-free strategy testing
- **A/B Testing**: Compare multiple strategies simultaneously
- **Auto-scaling**: Cloud deployment with auto-scaling

## Quick Start

### 1. Installation

```bash
git clone https://github.com/udooyy/trading-v-bot-2.0.git
cd trading-v-bot-2.0
pip install -r requirements.txt
```

### 2. Configuration

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

### 3. Run the Bot

```bash
python main.py
```

### 4. Setup TradingView Webhooks

1. Create a TradingView alert
2. Set webhook URL to: `http://your-server:8000/webhook/tradingview`
3. Use the webhook secret from your `.env` file

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_HOST` | API server host | No (default: 0.0.0.0) |
| `API_PORT` | API server port | No (default: 8000) |
| `SECRET_KEY` | JWT secret key | Yes |
| `DATABASE_URL` | Database connection URL | No (default: SQLite) |
| `BINANCE_API_KEY` | Binance API key | Yes (if using Binance) |
| `BINANCE_API_SECRET` | Binance API secret | Yes (if using Binance) |
| `TRADINGVIEW_WEBHOOK_SECRET` | TradingView webhook secret | Yes |
| `MAX_POSITION_SIZE` | Maximum position size (% of portfolio) | No (default: 0.1) |
| `STOP_LOSS_PERCENTAGE` | Default stop loss percentage | No (default: 0.02) |

### TradingView Alert Format

```json
{
  "symbol": "BTCUSDT",
  "action": "buy",
  "quantity": 0.1,
  "price": 45000,
  "stop_loss": 44000,
  "take_profit": 47000,
  "strategy": "ai_momentum",
  "timeframe": "1h"
}
```

## API Endpoints

### Trading Operations
- `POST /api/v1/trade` - Manual trade execution
- `GET /api/v1/positions` - Get current positions
- `POST /api/v1/close-position` - Close specific position

### Webhook Endpoints
- `POST /webhook/tradingview` - TradingView alerts
- `POST /webhook/exchange` - Exchange notifications

### Analytics
- `GET /api/v1/performance` - Trading performance metrics
- `GET /api/v1/trades` - Trade history
- `GET /api/v1/portfolio` - Portfolio overview

### AI/ML
- `POST /api/v1/analyze` - Technical analysis
- `GET /api/v1/predictions` - Price predictions
- `POST /api/v1/backtest` - Strategy backtesting

## Architecture

```
├── src/trading_bot/
│   ├── core/           # Core trading logic
│   ├── ai/             # AI/ML components
│   ├── exchanges/      # Exchange integrations
│   ├── webhooks/       # Webhook handlers
│   ├── database/       # Database models
│   ├── utils/          # Utility functions
│   └── api/            # FastAPI endpoints
├── tests/              # Test suite
├── config/             # Configuration files
└── logs/              # Log files
```

## Trading Strategies

### Built-in Strategies
1. **AI Momentum**: ML-based momentum detection
2. **Mean Reversion**: Statistical arbitrage
3. **Breakout Detection**: Chart pattern breakouts
4. **Grid Trading**: Automated grid strategies
5. **DCA (Dollar Cost Averaging)**: Systematic accumulation

### Custom Strategies
Create custom strategies by implementing the `BaseStrategy` class:

```python
from src.trading_bot.core.strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    async def analyze(self, data):
        # Your analysis logic
        return signal
    
    async def execute(self, signal):
        # Your execution logic
        pass
```

## Safety Features

- **Paper Trading Mode**: Test strategies without real money
- **Maximum Loss Limits**: Automatic trading halt on excessive losses
- **Position Size Limits**: Prevent over-leveraging
- **Exchange Rate Limits**: Respect API rate limits
- **Emergency Stop**: Manual override for all trading activities

## Monitoring & Alerts

### Web Dashboard
Access the web dashboard at `http://localhost:8000/dashboard` to monitor:
- Real-time P&L
- Active positions
- Recent trades
- AI predictions
- Risk metrics

### Notifications
Configure notifications for:
- Trade executions
- Profit targets hit
- Stop losses triggered
- System errors
- Daily/weekly reports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies and other financial instruments carries significant risk. Always do your own research and never invest more than you can afford to lose.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
4. Join our community Discord server

---

**⚠️ Risk Warning**: Automated trading involves substantial risk of loss. Past performance does not guarantee future results.