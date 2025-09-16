# Trading AI Bot for Alpaca

A Python-based algorithmic trading bot that uses Alpaca's API to execute trades based on a moving average crossover strategy.

## Features

- Real-time market data fetching from Alpaca
- Moving average crossover trading strategy
- Risk management (stop loss, position sizing)
- Paper trading support (recommended for testing)
- Configurable parameters

## Prerequisites

- Python 3.8+
- Alpaca account (free to sign up)
- Alpaca API keys

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/udooyy/trading-v-bot-2.0.git
   cd trading-v-bot-2.0
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Alpaca API keys:
   - Create a `.env` file in the project root
   - Add your Alpaca API credentials:
     ```
     ALPACA_API_KEY=your_api_key_here
     ALPACA_API_SECRET=your_api_secret_here
     ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Use paper trading for testing
     ```

## Configuration

Edit `config.py` to customize:

- **Trading Symbol**: Change `SYMBOL` (default: 'AAPL')
- **Timeframe**: Modify `TIMEFRAME` for different bar intervals
- **Moving Averages**: Adjust `SHORT_WINDOW` and `LONG_WINDOW`
- **Risk Management**: Configure `MAX_POSITION_SIZE`, `STOP_LOSS_PERCENTAGE`, `TAKE_PROFIT_PERCENTAGE`
- **Bot Settings**: Change `CHECK_INTERVAL` for trading frequency

## Usage

### Running the Bot

```bash
python bot.py
```

The bot will:
1. Connect to Alpaca's API
2. Fetch market data every minute
3. Calculate moving averages
4. Execute trades based on crossover signals
5. Log all activities

### Strategy Explanation

The bot uses a **Moving Average Crossover** strategy:
- **Buy Signal**: When the short MA crosses above the long MA
- **Sell Signal**: When the short MA crosses below the long MA

Default settings:
- Short MA: 5-period
- Long MA: 20-period
- Checks market every 60 seconds

## Safety Features

- **Paper Trading**: Use paper trading URL to test without real money
- **Position Limits**: Maximum position size configurable
- **Stop Loss**: Automatic loss protection
- **Error Handling**: Robust error handling and logging

## Risk Warning

⚠️ **This is for educational purposes only. Trading involves substantial risk of loss and is not suitable for every investor.**

- Start with paper trading
- Never risk more than you can afford to lose
- Backtest strategies thoroughly
- Monitor bot performance regularly

## API Reference

- [Alpaca Documentation](https://alpaca.markets/docs/)
- [Alpaca Python SDK](https://github.com/alpacahq/alpaca-trade-api-python)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details