"""Utility functions for the trading bot"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import yfinance as yf
from loguru import logger


def fetch_market_data(symbol: str, period: str = "1mo", interval: str = "1h") -> Optional[pd.DataFrame]:
    """Fetch market data using yfinance"""
    try:
        # Convert symbol format for yfinance
        yf_symbol = symbol.replace("USDT", "-USD").replace("BTC", "BTC").replace("ETH", "ETH")
        
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            logger.warning(f"No data found for {symbol}")
            return None
        
        # Rename columns to lowercase
        data.columns = [col.lower() for col in data.columns]
        
        # Reset index to have timestamp as column
        data.reset_index(inplace=True)
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        return None


def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for market data"""
    try:
        df = data.copy()
        
        # Simple Moving Averages
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # Exponential Moving Averages
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['close'] - df['bb_lower']) / df['bb_width']
        
        # Stochastic Oscillator
        high_14 = df['high'].rolling(window=14).max()
        low_14 = df['low'].rolling(window=14).min()
        df['stoch_k'] = 100 * (df['close'] - low_14) / (high_14 - low_14)
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        return df
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        return data


def calculate_position_size(
    account_balance: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """Calculate position size based on risk management"""
    try:
        risk_amount = account_balance * risk_per_trade
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff == 0:
            return 0.0
        
        position_size = risk_amount / price_diff
        return position_size
        
    except Exception as e:
        logger.error(f"Error calculating position size: {e}")
        return 0.0


def validate_trading_hours() -> bool:
    """Check if current time is within trading hours"""
    # For crypto, trading is 24/7, so always return True
    # For traditional markets, you would implement actual trading hours
    return True


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount for display"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "BTC":
        return f"{amount:.8f} BTC"
    elif currency == "ETH":
        return f"{amount:.6f} ETH"
    else:
        return f"{amount:.4f} {currency}"


def calculate_pnl(
    entry_price: float,
    current_price: float,
    quantity: float,
    side: str
) -> float:
    """Calculate profit and loss for a position"""
    try:
        if side.lower() == "long":
            pnl = (current_price - entry_price) * quantity
        elif side.lower() == "short":
            pnl = (entry_price - current_price) * quantity
        else:
            pnl = 0.0
        
        return pnl
        
    except Exception as e:
        logger.error(f"Error calculating PnL: {e}")
        return 0.0


def calculate_win_rate(trades: List[Dict]) -> float:
    """Calculate win rate from trade history"""
    try:
        if not trades:
            return 0.0
        
        winning_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
        return (winning_trades / len(trades)) * 100
        
    except Exception as e:
        logger.error(f"Error calculating win rate: {e}")
        return 0.0


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio"""
    try:
        if len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate / 252  # Daily risk-free rate
        
        if np.std(excess_returns) == 0:
            return 0.0
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return sharpe
        
    except Exception as e:
        logger.error(f"Error calculating Sharpe ratio: {e}")
        return 0.0


def calculate_max_drawdown(equity_curve: List[float]) -> float:
    """Calculate maximum drawdown"""
    try:
        if len(equity_curve) < 2:
            return 0.0
        
        equity_array = np.array(equity_curve)
        peak = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - peak) / peak
        max_drawdown = np.min(drawdown)
        
        return abs(max_drawdown) * 100  # Return as percentage
        
    except Exception as e:
        logger.error(f"Error calculating max drawdown: {e}")
        return 0.0


def generate_trade_id() -> str:
    """Generate unique trade ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"trade_{timestamp}"


def is_market_open(symbol: str) -> bool:
    """Check if market is open for given symbol"""
    # For crypto markets, always open
    if any(crypto in symbol.upper() for crypto in ['BTC', 'ETH', 'USDT', 'BUSD']):
        return True
    
    # For traditional markets, check trading hours
    # This is a simplified implementation
    now = datetime.utcnow()
    weekday = now.weekday()
    
    # Monday = 0, Sunday = 6
    if weekday >= 5:  # Weekend
        return False
    
    # Simplified market hours (9:30 AM - 4:00 PM ET)
    # This should be improved for different markets and time zones
    hour = now.hour
    return 14 <= hour <= 21  # UTC time for US market hours


def convert_timeframe(timeframe: str) -> str:
    """Convert timeframe to exchange format"""
    timeframe_map = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '30m': '30m',
        '1h': '1h',
        '4h': '4h',
        '1d': '1d',
        '1w': '1w'
    }
    return timeframe_map.get(timeframe, '1h')


def create_sample_data(symbol: str, days: int = 30) -> pd.DataFrame:
    """Create sample market data for testing"""
    try:
        # Generate dates
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='1H')
        
        # Generate random price data
        np.random.seed(42)  # For reproducible results
        base_price = 50000 if 'BTC' in symbol else 2500  # Different base prices
        
        # Generate random walk
        returns = np.random.normal(0, 0.02, len(date_range))
        prices = [base_price]
        
        for i in range(1, len(returns)):
            new_price = prices[-1] * (1 + returns[i])
            prices.append(max(new_price, base_price * 0.5))  # Prevent negative prices
        
        # Create OHLCV data
        data = []
        for i, (timestamp, price) in enumerate(zip(date_range, prices)):
            high = price * (1 + abs(np.random.normal(0, 0.01)))
            low = price * (1 - abs(np.random.normal(0, 0.01)))
            open_price = prices[i-1] if i > 0 else price
            close_price = price
            volume = abs(np.random.normal(1000, 300))
            
            data.append({
                'datetime': timestamp,
                'open': open_price,
                'high': max(open_price, high, close_price),
                'low': min(open_price, low, close_price),
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        return df
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        return pd.DataFrame()