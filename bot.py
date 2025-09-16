import time
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from alpaca_trade_api import REST, TimeFrame
import config

# Import RL agent
from rl_agent import QLearningAgent

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlpacaTradingBot:
    def backtest(self, days=30):
        """Backtest RL agent on historical data."""
        logger.info(f"Starting backtest for {days} days...")
        data = self.get_historical_data(self.symbol, days=days)
        if data.empty or len(data) < config.LONG_WINDOW:
            logger.warning("Not enough data for backtesting.")
            return

        # Simulate trading over historical data
        position = 0
        entry_price = None
        total_reward = 0
        for i in range(config.LONG_WINDOW, len(data)):
            window = data.iloc[:i+1]
            short_ma, long_ma = self.calculate_moving_averages(window)
            momentum = self.calculate_momentum(window)
            rsi = self.calculate_rsi(window)
            volatility = self.calculate_volatility(window)
            ts = window['timestamp'].iloc[-1]
            time_of_day = ts.hour + ts.minute / 60.0
            current_price = window['close'].iloc[-1]
            # Expanded state
            state = np.array([short_ma, long_ma, position, momentum, rsi, volatility, time_of_day])
            action = self.agent.act(state)
            action_name = self.action_map[action]
            reward = 0
            # Penalties
            inactivity_penalty = -0.01
            holding_penalty = 0
            overtrade_penalty = -0.05 if action_name in ['buy', 'sell'] else 0
            prev_position = position
            prev_entry_price = entry_price
            # Simulate action
            if action_name == 'buy' and position <= 0:
                position = 1
                entry_price = current_price
            elif action_name == 'sell' and position > 0:
                reward = (current_price - entry_price) * abs(prev_position)
                position = 0
                entry_price = None
            # Holding penalty
            if position > 0 and entry_price is not None and current_price < entry_price:
                holding_penalty = -abs(current_price - entry_price) * 0.1
            reward += inactivity_penalty + holding_penalty + overtrade_penalty
            # Next state
            next_state = state  # For simplicity, use current state as next
            # Learn
            if action_name == 'sell' and prev_entry_price is not None:
                self.agent.remember(state, action, reward, next_state, False)
            total_reward += reward
        logger.info(f"Backtest complete. Total reward: {total_reward:.2f}")
    def calculate_momentum(self, data, window=5):
        if data.empty or len(data) < window + 1:
            return 0.0
        return data['close'].iloc[-1] - data['close'].iloc[-window-1]

    def calculate_rsi(self, data, window=14):
        if data.empty or len(data) < window + 1:
            return 50.0
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean().iloc[-1]
        if loss == 0:
            return 100.0
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_volatility(self, data, window=10):
        if data.empty or len(data) < window:
            return 0.0
        return data['close'].pct_change().rolling(window=window).std().iloc[-1]
    def __init__(self):
        self.api = REST(config.API_KEY, config.API_SECRET, config.BASE_URL)
        self.symbol = config.SYMBOL
        self.position = 0
        self.cash = 0
        self.entry_price = None  # Track entry price for reward calculation
        # RL agent: state = [short_ma, long_ma, position, momentum, rsi, volatility, time_of_day], actions = [hold, buy, sell]
        self.agent = QLearningAgent(
            state_size=7,
            action_size=3,
            alpha=config.QL_ALPHA,
            gamma=config.QL_GAMMA,
            epsilon=config.QL_EPSILON,
            epsilon_min=config.QL_EPSILON_MIN,
            epsilon_decay=config.QL_EPSILON_DECAY,
            replay_capacity=config.QL_REPLAY_CAPACITY,
            batch_size=config.QL_BATCH_SIZE
        )
        self.action_map = {0: 'hold', 1: 'buy', 2: 'sell'}
        logger.info("Trading bot initialized")

    def get_historical_data(self, symbol, days=30):
        """Fetch historical market data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            bars = self.api.get_bars(
                symbol,
                TimeFrame.Minute,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                limit=1000
            ).df

            if bars.empty:
                logger.warning(f"No data received for {symbol}")
                return pd.DataFrame()

            # Reset index to have datetime as column
            bars = bars.reset_index()
            bars['timestamp'] = bars['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
            return bars

        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()

    def calculate_moving_averages(self, data):
        """Calculate short and long moving averages"""
        if data.empty or len(data) < config.LONG_WINDOW:
            return None, None

        short_ma = data['close'].rolling(window=config.SHORT_WINDOW).mean().iloc[-1]
        long_ma = data['close'].rolling(window=config.LONG_WINDOW).mean().iloc[-1]

        return short_ma, long_ma

    def get_current_position(self):
        """Get current position for the symbol"""
        try:
            position = self.api.get_position(self.symbol)
            return int(position.qty)
        except Exception as e:
            logger.debug(f"No position found for {self.symbol}: {e}")
            return 0

    def get_account_info(self):
        """Get account information"""
        try:
            account = self.api.get_account()
            return {
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity)
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None

    def place_order(self, side, qty, order_type='market'):
        """Place a trading order"""
        try:
            order = self.api.submit_order(
                symbol=self.symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force='gtc'
            )
            logger.info(f"Order placed: {side} {qty} {self.symbol} at market price")
            return order
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    def trading_strategy(self):
        """RL-based trading strategy with expanded state"""
        data = self.get_historical_data(self.symbol, days=1)
        if data.empty:
            return

        short_ma, long_ma = self.calculate_moving_averages(data)
        momentum = self.calculate_momentum(data)
        rsi = self.calculate_rsi(data)
        volatility = self.calculate_volatility(data)
        now = datetime.now()
        time_of_day = now.hour + now.minute / 60.0  # e.g., 13.5 for 1:30pm

        if short_ma is None or long_ma is None:
            return

        current_price = data['close'].iloc[-1]
        position = self.get_current_position()

        # Expanded state: [short_ma, long_ma, position, momentum, rsi, volatility, time_of_day]
        state = np.array([short_ma, long_ma, position, momentum, rsi, volatility, time_of_day])

        # RL agent chooses action
        action = self.agent.act(state)
        action_name = self.action_map[action]
        reward = 0
        done = False
        qty = min(config.MAX_POSITION_SIZE, int(self.get_account_info()['cash'] / current_price))

        # Track previous position for reward
        prev_position = position
        prev_entry_price = self.entry_price

        # Penalty for inactivity (small negative reward for holding)
        inactivity_penalty = -0.01
        # Penalty for holding a losing position
        holding_penalty = 0
        # Penalty for overtrading (small negative reward for every trade)
        overtrade_penalty = -0.05 if action_name in ['buy', 'sell'] else 0

        # Execute action and set entry price
        stop_loss_triggered = False
        take_profit_triggered = False
        # Check stop-loss/take-profit if holding a position
        if position > 0 and self.entry_price is not None:
            stop_loss_price = self.entry_price * (1 - config.STOP_LOSS_PERCENTAGE)
            take_profit_price = self.entry_price * (1 + config.TAKE_PROFIT_PERCENTAGE)
            if current_price <= stop_loss_price:
                self.place_order('sell', abs(position))
                logger.info(f"STOP-LOSS: Selling {abs(position)} shares at {current_price}")
                stop_loss_triggered = True
                reward = (current_price - self.entry_price) * abs(position)
                self.entry_price = None
            elif current_price >= take_profit_price:
                self.place_order('sell', abs(position))
                logger.info(f"TAKE-PROFIT: Selling {abs(position)} shares at {current_price}")
                take_profit_triggered = True
                reward = (current_price - self.entry_price) * abs(position)
                self.entry_price = None

        # Only allow buy if not exceeding max position size
        if not stop_loss_triggered and not take_profit_triggered:
            if action_name == 'buy' and qty > 0 and position <= 0:
                if qty <= config.MAX_POSITION_SIZE:
                    self.place_order('buy', qty)
                    self.entry_price = current_price
                    logger.info(f"RL BUY: {qty} shares at {current_price}")
            elif action_name == 'sell' and position > 0:
                self.place_order('sell', abs(position))
                logger.info(f"RL SELL: {abs(position)} shares at {current_price}")
                # Reward: profit/loss from trade
                if prev_entry_price is not None:
                    reward = (current_price - prev_entry_price) * abs(prev_position)
                self.entry_price = None
            else:
                logger.info("RL HOLD")
                # If holding a position and it's losing, penalize
                if position > 0 and self.entry_price is not None and current_price < self.entry_price:
                    holding_penalty = -abs(current_price - self.entry_price) * 0.1

        # Add penalties to reward
        reward += inactivity_penalty + holding_penalty + overtrade_penalty

        # Wait for next state
        time.sleep(1)
        next_data = self.get_historical_data(self.symbol, days=1)
        next_short_ma, next_long_ma = self.calculate_moving_averages(next_data)
        next_momentum = self.calculate_momentum(next_data)
        next_rsi = self.calculate_rsi(next_data)
        next_volatility = self.calculate_volatility(next_data)
        next_time_of_day = datetime.now().hour + datetime.now().minute / 60.0
        next_position = self.get_current_position()
        next_state = np.array([
            next_short_ma, next_long_ma, next_position, next_momentum, next_rsi, next_volatility, next_time_of_day
        ]) if next_short_ma and next_long_ma else state

        # RL agent learns only if trade was closed (sell)
        if action_name == 'sell' and prev_entry_price is not None:
            self.agent.remember(state, action, reward, next_state, done)
            self.agent.save()

    def run(self):
        """Main bot loop"""
        logger.info("Starting trading bot...")

        while True:
            try:
                self.trading_strategy()
                time.sleep(config.CHECK_INTERVAL)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    bot = AlpacaTradingBot()
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'backtest':
        bot.backtest(days=30)
    else:
        bot.run()