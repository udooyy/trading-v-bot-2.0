import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Alpaca API Configuration
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_API_SECRET')
BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')  # Use paper trading by default

# Trading Configuration
SYMBOL = 'AAPL'  # Default trading symbol
TIMEFRAME = '1Min'  # 1 minute bars
SHORT_WINDOW = 5  # Short moving average window
LONG_WINDOW = 20  # Long moving average window

# Risk Management
MAX_POSITION_SIZE = 100  # Maximum shares to hold
STOP_LOSS_PERCENTAGE = 0.02  # 2% stop loss
TAKE_PROFIT_PERCENTAGE = 0.05  # 5% take profit

# Bot Configuration
CHECK_INTERVAL = 60  # Check market every 60 seconds
LOG_LEVEL = 'INFO'

# Q-Learning Parameters
QL_ALPHA = 0.1  # Learning rate
QL_GAMMA = 0.95  # Discount factor
QL_EPSILON = 1.0  # Exploration rate
QL_EPSILON_MIN = 0.01
QL_EPSILON_DECAY = 0.995
QL_REPLAY_CAPACITY = 1000
QL_BATCH_SIZE = 32