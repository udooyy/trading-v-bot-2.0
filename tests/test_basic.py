"""Basic tests for the trading bot"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch
import pandas as pd

from src.trading_bot.core.config import get_settings
from src.trading_bot.core.bot import TradingBot
from src.trading_bot.webhooks.tradingview import TradingViewWebhook, SignalValidator
from src.trading_bot.utils.helpers import calculate_technical_indicators, create_sample_data


@pytest.fixture
def sample_market_data():
    """Create sample market data for testing"""
    return create_sample_data("BTCUSDT", days=10)


@pytest.fixture
def trading_bot():
    """Create trading bot instance for testing"""
    return TradingBot()


@pytest.fixture
def webhook_handler():
    """Create webhook handler for testing"""
    return TradingViewWebhook()


@pytest.fixture
def signal_validator():
    """Create signal validator for testing"""
    return SignalValidator()


def test_settings_loading():
    """Test settings loading"""
    settings = get_settings()
    assert settings.API_HOST == "0.0.0.0"
    assert settings.API_PORT == 8000
    assert settings.PAPER_TRADING == True


def test_technical_indicators(sample_market_data):
    """Test technical indicators calculation"""
    data_with_indicators = calculate_technical_indicators(sample_market_data)
    
    # Check that indicators were added
    expected_columns = ['sma_10', 'sma_20', 'rsi', 'macd', 'bb_upper', 'bb_lower']
    for col in expected_columns:
        assert col in data_with_indicators.columns
    
    # Check RSI values are within expected range
    rsi_values = data_with_indicators['rsi'].dropna()
    assert all(0 <= rsi <= 100 for rsi in rsi_values)


def test_signal_validation(signal_validator):
    """Test signal validation"""
    # Valid signal
    valid_signal = {
        'symbol': 'BTCUSDT',
        'action': 'buy',
        'quantity': 0.1,
        'price': 50000.0
    }
    assert signal_validator.validate_signal(valid_signal) == True
    
    # Invalid signal - missing symbol
    invalid_signal = {
        'action': 'buy',
        'quantity': 0.1
    }
    assert signal_validator.validate_signal(invalid_signal) == False
    
    # Invalid signal - invalid action
    invalid_action_signal = {
        'symbol': 'BTCUSDT',
        'action': 'invalid_action',
        'quantity': 0.1
    }
    assert signal_validator.validate_signal(invalid_action_signal) == False


def test_tradingview_webhook_parsing(webhook_handler):
    """Test TradingView webhook parsing"""
    # Test simple signal
    simple_payload = {
        'symbol': 'BTCUSDT',
        'action': 'buy',
        'quantity': 0.1
    }
    
    parsed_signal = webhook_handler.parse_tradingview_signal(simple_payload)
    assert parsed_signal is not None
    assert parsed_signal['symbol'] == 'BTCUSDT'
    assert parsed_signal['action'] == 'buy'
    assert parsed_signal['quantity'] == 0.1
    
    # Test comprehensive signal
    comprehensive_payload = {
        'symbol': 'ETHUSDT',
        'action': 'long',
        'quantity': 0.5,
        'price': 2500.0,
        'stop_loss': 2400.0,
        'take_profit': 2700.0,
        'strategy': 'breakout',
        'confidence': 0.85
    }
    
    parsed_signal = webhook_handler.parse_tradingview_signal(comprehensive_payload)
    assert parsed_signal is not None
    assert parsed_signal['symbol'] == 'ETHUSDT'
    assert parsed_signal['action'] == 'long'
    assert parsed_signal['stop_loss'] == 2400.0
    assert parsed_signal['take_profit'] == 2700.0


def test_signal_sanitization(signal_validator):
    """Test signal sanitization"""
    raw_signal = {
        'symbol': 'btc/usdt',
        'action': 'BUY',
        'quantity': '0.1',
        'price': '50000.50'
    }
    
    sanitized = signal_validator.sanitize_signal(raw_signal)
    
    assert sanitized['symbol'] == 'BTCUSDT'
    assert sanitized['action'] == 'buy'
    assert sanitized['quantity'] == 0.1
    assert sanitized['price'] == 50000.50
    assert sanitized['confidence'] == 1.0


@pytest.mark.asyncio
async def test_trading_bot_initialization(trading_bot):
    """Test trading bot initialization"""
    # Mock the dependencies to avoid actual API calls
    with patch.object(trading_bot.exchange_manager, 'initialize'), \
         patch.object(trading_bot.strategy_manager, 'initialize'), \
         patch.object(trading_bot.ai_generator, 'initialize'), \
         patch.object(trading_bot.portfolio, 'initialize'):
        
        await trading_bot.initialize()
        assert trading_bot.exchange_manager is not None
        assert trading_bot.strategy_manager is not None


@pytest.mark.asyncio
async def test_signal_processing(trading_bot):
    """Test signal processing"""
    # Mock dependencies
    with patch.object(trading_bot.risk_manager, 'validate_trade', return_value=True), \
         patch.object(trading_bot.risk_manager, 'calculate_position_size', return_value=0.1), \
         patch.object(trading_bot.exchange_manager, 'place_order') as mock_place_order:
        
        mock_place_order.return_value = {
            'id': 'test_order_123',
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'amount': 0.1,
            'price': 50000.0
        }
        
        test_signal = {
            'symbol': 'BTCUSDT',
            'action': 'buy',
            'quantity': 0.1,
            'strategy': 'test'
        }
        
        await trading_bot.process_tradingview_signal(test_signal)
        
        # Verify that the order was placed
        mock_place_order.assert_called_once()


def test_example_alerts(webhook_handler):
    """Test example alert formats"""
    examples = webhook_handler.create_example_alerts()
    
    assert 'simple_buy' in examples
    assert 'comprehensive_signal' in examples
    assert 'close_position' in examples
    
    # Test parsing example alerts
    for example_name, example_payload in examples.items():
        if example_name != 'message_format':  # Skip message format for now
            parsed = webhook_handler.parse_tradingview_signal(example_payload)
            assert parsed is not None, f"Failed to parse {example_name}"


def test_create_sample_data():
    """Test sample data creation"""
    data = create_sample_data("BTCUSDT", days=5)
    
    assert not data.empty
    assert 'open' in data.columns
    assert 'high' in data.columns
    assert 'low' in data.columns
    assert 'close' in data.columns
    assert 'volume' in data.columns
    
    # Check data integrity
    for _, row in data.iterrows():
        assert row['low'] <= row['open'] <= row['high']
        assert row['low'] <= row['close'] <= row['high']
        assert row['volume'] > 0


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])