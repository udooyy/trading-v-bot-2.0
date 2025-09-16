"""TradingView webhook handlers"""

import json
import hmac
import hashlib
from typing import Dict, Optional
from fastapi import HTTPException
from loguru import logger
from ..core.config import get_settings


class TradingViewWebhook:
    """Handle TradingView webhook signals"""
    
    def __init__(self):
        self.settings = get_settings()
        
    def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """Validate webhook signature for security"""
        if not self.settings.TRADINGVIEW_WEBHOOK_SECRET:
            logger.warning("No webhook secret configured - skipping signature validation")
            return True
        
        try:
            expected_signature = hmac.new(
                self.settings.TRADINGVIEW_WEBHOOK_SECRET.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False
    
    def parse_tradingview_signal(self, payload: Dict) -> Optional[Dict]:
        """Parse TradingView alert payload into standardized signal format"""
        try:
            # Standard TradingView alert format
            signal = {
                'symbol': payload.get('symbol', '').upper(),
                'action': payload.get('action', '').lower(),
                'price': payload.get('price'),
                'quantity': payload.get('quantity'),
                'stop_loss': payload.get('stop_loss'),
                'take_profit': payload.get('take_profit'),
                'strategy': payload.get('strategy', 'tradingview'),
                'timeframe': payload.get('timeframe', '1h'),
                'timestamp': payload.get('timestamp'),
                'confidence': payload.get('confidence', 1.0),
                'exchange': payload.get('exchange', 'binance')
            }
            
            # Validate required fields
            if not signal['symbol'] or not signal['action']:
                logger.error("Missing required fields: symbol or action")
                return None
            
            # Validate action
            valid_actions = ['buy', 'sell', 'long', 'short', 'close', 'exit']
            if signal['action'] not in valid_actions:
                logger.error(f"Invalid action: {signal['action']}")
                return None
            
            # Set default quantity if not provided
            if not signal['quantity']:
                signal['quantity'] = self.settings.MAX_POSITION_SIZE
            
            # Parse additional fields from message if present
            message = payload.get('message', '')
            if message:
                parsed_message = self._parse_alert_message(message)
                signal.update(parsed_message)
            
            logger.info(f"Parsed TradingView signal: {signal}")
            return signal
            
        except Exception as e:
            logger.error(f"Error parsing TradingView signal: {e}")
            return None
    
    def _parse_alert_message(self, message: str) -> Dict:
        """Parse additional information from alert message"""
        parsed = {}
        
        try:
            # Try to parse as JSON first
            parsed_json = json.loads(message)
            if isinstance(parsed_json, dict):
                return parsed_json
        except:
            pass
        
        # Parse text-based alert messages
        lines = message.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                # Try to convert to appropriate type
                try:
                    if '.' in value:
                        parsed[key] = float(value)
                    elif value.isdigit():
                        parsed[key] = int(value)
                    else:
                        parsed[key] = value
                except:
                    parsed[key] = value
        
        return parsed
    
    def create_example_alerts(self) -> Dict[str, Dict]:
        """Create example alert formats for documentation"""
        return {
            'simple_buy': {
                'symbol': 'BTCUSDT',
                'action': 'buy',
                'quantity': 0.1
            },
            'comprehensive_signal': {
                'symbol': 'ETHUSDT',
                'action': 'long',
                'quantity': 0.5,
                'price': 2500.0,
                'stop_loss': 2400.0,
                'take_profit': 2700.0,
                'strategy': 'breakout',
                'timeframe': '4h',
                'confidence': 0.85
            },
            'close_position': {
                'symbol': 'BTCUSDT',
                'action': 'close',
                'strategy': 'manual_exit'
            },
            'message_format': {
                'symbol': 'ADAUSDT',
                'action': 'buy',
                'message': '''
                Entry: 0.45
                Stop Loss: 0.43
                Take Profit: 0.50
                Risk: 2%
                Strategy: RSI Divergence
                '''
            }
        }


class SignalValidator:
    """Validate trading signals before execution"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def validate_signal(self, signal: Dict) -> bool:
        """Validate trading signal"""
        try:
            # Check required fields
            required_fields = ['symbol', 'action']
            for field in required_fields:
                if field not in signal or not signal[field]:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate symbol format
            if not self._validate_symbol(signal['symbol']):
                return False
            
            # Validate action
            valid_actions = ['buy', 'sell', 'long', 'short', 'close', 'exit']
            if signal['action'] not in valid_actions:
                logger.error(f"Invalid action: {signal['action']}")
                return False
            
            # Validate quantity
            if 'quantity' in signal and signal['quantity']:
                quantity = float(signal['quantity'])
                if quantity <= 0 or quantity > self.settings.MAX_POSITION_SIZE:
                    logger.error(f"Invalid quantity: {quantity}")
                    return False
            
            # Validate prices
            price_fields = ['price', 'stop_loss', 'take_profit']
            for field in price_fields:
                if field in signal and signal[field]:
                    try:
                        price = float(signal[field])
                        if price <= 0:
                            logger.error(f"Invalid {field}: {price}")
                            return False
                    except (ValueError, TypeError):
                        logger.error(f"Invalid {field} format: {signal[field]}")
                        return False
            
            # Validate stop loss and take profit relationship
            if signal.get('price') and signal.get('stop_loss') and signal.get('take_profit'):
                price = float(signal['price'])
                stop_loss = float(signal['stop_loss'])
                take_profit = float(signal['take_profit'])
                
                if signal['action'] in ['buy', 'long']:
                    if stop_loss >= price:
                        logger.error("Stop loss should be below entry price for long positions")
                        return False
                    if take_profit <= price:
                        logger.error("Take profit should be above entry price for long positions")
                        return False
                elif signal['action'] in ['sell', 'short']:
                    if stop_loss <= price:
                        logger.error("Stop loss should be above entry price for short positions")
                        return False
                    if take_profit >= price:
                        logger.error("Take profit should be below entry price for short positions")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return False
    
    def _validate_symbol(self, symbol: str) -> bool:
        """Validate trading symbol format"""
        if not symbol or len(symbol) < 3:
            logger.error(f"Invalid symbol format: {symbol}")
            return False
        
        # Common symbol formats: BTCUSDT, BTC/USDT, BTC-USDT
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/-')
        if not all(c in valid_chars for c in symbol.upper()):
            logger.error(f"Invalid characters in symbol: {symbol}")
            return False
        
        return True
    
    def sanitize_signal(self, signal: Dict) -> Dict:
        """Sanitize and normalize signal data"""
        sanitized = signal.copy()
        
        # Normalize symbol format
        if 'symbol' in sanitized:
            sanitized['symbol'] = sanitized['symbol'].upper().replace('/', '').replace('-', '')
        
        # Normalize action
        if 'action' in sanitized:
            sanitized['action'] = sanitized['action'].lower()
        
        # Ensure numeric fields are properly typed
        numeric_fields = ['quantity', 'price', 'stop_loss', 'take_profit', 'confidence']
        for field in numeric_fields:
            if field in sanitized and sanitized[field] is not None:
                try:
                    sanitized[field] = float(sanitized[field])
                except (ValueError, TypeError):
                    sanitized[field] = None
        
        # Set defaults
        if 'confidence' not in sanitized or sanitized['confidence'] is None:
            sanitized['confidence'] = 1.0
        
        if 'strategy' not in sanitized:
            sanitized['strategy'] = 'tradingview'
        
        return sanitized