"""Core trading bot implementation"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from loguru import logger

from .config import get_settings
from .strategy import StrategyManager
from .risk_manager import RiskManager
from .portfolio import Portfolio
from ..exchanges.exchange_manager import ExchangeManager
from ..ai.signal_generator import AISignalGenerator
from ..database.models import Trade, Position


class TradingBot:
    """Main trading bot class"""
    
    def __init__(self):
        self.settings = get_settings()
        self.is_running = False
        self.exchange_manager = ExchangeManager()
        self.strategy_manager = StrategyManager()
        self.risk_manager = RiskManager()
        self.portfolio = Portfolio()
        self.ai_generator = AISignalGenerator()
        
        # Trading state
        self.active_positions: Dict[str, Position] = {}
        self.pending_orders: Dict[str, dict] = {}
        
    async def initialize(self):
        """Initialize the trading bot"""
        logger.info("Initializing trading bot...")
        
        # Initialize components
        await self.exchange_manager.initialize()
        await self.strategy_manager.initialize()
        await self.ai_generator.initialize()
        await self.portfolio.initialize()
        
        logger.info("Trading bot initialized successfully")
    
    async def start(self):
        """Start the trading bot"""
        self.is_running = True
        logger.info("Starting trading bot...")
        
        # Start main trading loop
        while self.is_running:
            try:
                await self._trading_cycle()
                await asyncio.sleep(60)  # Run cycle every minute
            except Exception as e:
                logger.error(f"Error in trading cycle: {e}")
                await asyncio.sleep(30)
    
    async def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping trading bot...")
        self.is_running = False
        
        # Close all positions if needed
        await self._emergency_stop()
    
    async def _trading_cycle(self):
        """Main trading cycle"""
        # Update market data
        await self._update_market_data()
        
        # Generate AI signals
        signals = await self.ai_generator.generate_signals()
        
        # Process signals through strategies
        for signal in signals:
            await self._process_signal(signal)
        
        # Update portfolio
        await self.portfolio.update()
        
        # Check and manage existing positions
        await self._manage_positions()
    
    async def _update_market_data(self):
        """Update market data for all tracked symbols"""
        # Implementation for updating market data
        pass
    
    async def _process_signal(self, signal: dict):
        """Process a trading signal"""
        symbol = signal.get('symbol')
        action = signal.get('action')
        
        # Risk check
        if not await self.risk_manager.validate_trade(signal):
            logger.warning(f"Trade rejected by risk manager: {signal}")
            return
        
        # Execute trade based on signal
        if action in ['buy', 'long']:
            await self._execute_buy(signal)
        elif action in ['sell', 'short']:
            await self._execute_sell(signal)
        elif action == 'close':
            await self._close_position(symbol)
    
    async def _execute_buy(self, signal: dict):
        """Execute a buy order"""
        symbol = signal['symbol']
        
        # Calculate position size
        position_size = await self.risk_manager.calculate_position_size(signal)
        
        if position_size <= 0:
            logger.warning(f"Invalid position size for {symbol}: {position_size}")
            return
        
        # Place order through exchange
        order = await self.exchange_manager.place_order(
            symbol=symbol,
            side='buy',
            amount=position_size,
            order_type='market'
        )
        
        if order:
            logger.info(f"Buy order placed: {order}")
            await self._track_position(order, signal)
    
    async def _execute_sell(self, signal: dict):
        """Execute a sell order"""
        symbol = signal['symbol']
        
        # Check if we have a position to sell
        if symbol not in self.active_positions:
            logger.warning(f"No position to sell for {symbol}")
            return
        
        position = self.active_positions[symbol]
        
        # Place sell order
        order = await self.exchange_manager.place_order(
            symbol=symbol,
            side='sell',
            amount=position.quantity,
            order_type='market'
        )
        
        if order:
            logger.info(f"Sell order placed: {order}")
            await self._close_position(symbol)
    
    async def _close_position(self, symbol: str):
        """Close a position"""
        if symbol in self.active_positions:
            position = self.active_positions[symbol]
            
            # Place closing order
            order = await self.exchange_manager.place_order(
                symbol=symbol,
                side='sell' if position.side == 'long' else 'buy',
                amount=position.quantity,
                order_type='market'
            )
            
            if order:
                del self.active_positions[symbol]
                logger.info(f"Position closed for {symbol}")
    
    async def _track_position(self, order: dict, signal: dict):
        """Track a new position"""
        symbol = signal['symbol']
        
        position = Position(
            symbol=symbol,
            side='long',  # Assuming long positions for now
            quantity=order['amount'],
            entry_price=order['price'],
            stop_loss=signal.get('stop_loss'),
            take_profit=signal.get('take_profit'),
            timestamp=datetime.utcnow()
        )
        
        self.active_positions[symbol] = position
    
    async def _manage_positions(self):
        """Manage existing positions (stop loss, take profit)"""
        for symbol, position in list(self.active_positions.items()):
            current_price = await self.exchange_manager.get_current_price(symbol)
            
            if current_price:
                # Check stop loss
                if position.stop_loss and current_price <= position.stop_loss:
                    await self._close_position(symbol)
                    logger.info(f"Stop loss triggered for {symbol}")
                
                # Check take profit
                elif position.take_profit and current_price >= position.take_profit:
                    await self._close_position(symbol)
                    logger.info(f"Take profit triggered for {symbol}")
    
    async def _emergency_stop(self):
        """Emergency stop - close all positions"""
        logger.warning("Emergency stop activated - closing all positions")
        
        for symbol in list(self.active_positions.keys()):
            await self._close_position(symbol)
    
    async def process_tradingview_signal(self, signal: dict):
        """Process a signal from TradingView webhook"""
        logger.info(f"Received TradingView signal: {signal}")
        
        # Validate signal format
        required_fields = ['symbol', 'action']
        if not all(field in signal for field in required_fields):
            logger.error(f"Invalid signal format: missing required fields")
            return
        
        # Add to processing queue
        await self._process_signal(signal)
    
    def get_status(self) -> dict:
        """Get bot status"""
        return {
            'is_running': self.is_running,
            'active_positions': len(self.active_positions),
            'portfolio_value': self.portfolio.get_total_value(),
            'daily_pnl': self.portfolio.get_daily_pnl(),
            'uptime': datetime.utcnow().isoformat()
        }