"""Exchange management for multiple trading platforms"""

import ccxt
from typing import Dict, Optional, List
import asyncio
from loguru import logger
from ..core.config import get_settings


class ExchangeManager:
    """Manages connections to multiple exchanges"""
    
    def __init__(self):
        self.settings = get_settings()
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.default_exchange = self.settings.DEFAULT_EXCHANGE
        
    async def initialize(self):
        """Initialize exchange connections"""
        logger.info("Initializing exchange connections...")
        
        # Initialize Binance if credentials are provided
        if self.settings.BINANCE_API_KEY and self.settings.BINANCE_API_SECRET:
            await self._initialize_binance()
        
        logger.info(f"Exchange manager initialized with {len(self.exchanges)} exchanges")
    
    async def _initialize_binance(self):
        """Initialize Binance exchange"""
        try:
            binance_config = {
                'apiKey': self.settings.BINANCE_API_KEY,
                'secret': self.settings.BINANCE_API_SECRET,
                'sandbox': self.settings.BINANCE_SANDBOX,
                'enableRateLimit': True,
            }
            
            if self.settings.PAPER_TRADING:
                # Use sandbox for paper trading
                binance_config['sandbox'] = True
            
            self.exchanges['binance'] = ccxt.binance(binance_config)
            
            # Test connection
            await self._test_exchange_connection('binance')
            
            logger.info("Binance exchange initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Binance: {e}")
    
    async def _test_exchange_connection(self, exchange_name: str):
        """Test exchange connection"""
        try:
            exchange = self.exchanges[exchange_name]
            balance = await exchange.fetch_balance()
            logger.info(f"{exchange_name} connection test successful")
        except Exception as e:
            logger.error(f"{exchange_name} connection test failed: {e}")
            raise
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        order_type: str = 'market',
        price: Optional[float] = None,
        exchange: Optional[str] = None
    ) -> Optional[dict]:
        """Place an order on the exchange"""
        exchange_name = exchange or self.default_exchange
        
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not available")
            return None
        
        try:
            if self.settings.PAPER_TRADING:
                # Simulate order for paper trading
                return await self._simulate_order(symbol, side, amount, order_type, price)
            
            exchange_obj = self.exchanges[exchange_name]
            
            if order_type == 'market':
                if side == 'buy':
                    order = await exchange_obj.create_market_buy_order(symbol, amount)
                else:
                    order = await exchange_obj.create_market_sell_order(symbol, amount)
            elif order_type == 'limit' and price:
                if side == 'buy':
                    order = await exchange_obj.create_limit_buy_order(symbol, amount, price)
                else:
                    order = await exchange_obj.create_limit_sell_order(symbol, amount, price)
            else:
                logger.error(f"Invalid order type or missing price: {order_type}")
                return None
            
            logger.info(f"Order placed: {order}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    async def _simulate_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        order_type: str,
        price: Optional[float]
    ) -> dict:
        """Simulate order execution for paper trading"""
        current_price = await self.get_current_price(symbol)
        
        if not current_price:
            current_price = price or 50000  # Fallback price
        
        # Simulate order
        simulated_order = {
            'id': f'sim_{asyncio.get_event_loop().time()}',
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': current_price,
            'type': order_type,
            'status': 'closed',
            'filled': amount,
            'timestamp': asyncio.get_event_loop().time(),
            'simulated': True
        }
        
        logger.info(f"Simulated order: {simulated_order}")
        return simulated_order
    
    async def get_current_price(self, symbol: str, exchange: Optional[str] = None) -> Optional[float]:
        """Get current price for a symbol"""
        exchange_name = exchange or self.default_exchange
        
        if exchange_name not in self.exchanges:
            return None
        
        try:
            exchange_obj = self.exchanges[exchange_name]
            ticker = await exchange_obj.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    async def get_balance(self, exchange: Optional[str] = None) -> Optional[dict]:
        """Get account balance"""
        exchange_name = exchange or self.default_exchange
        
        if exchange_name not in self.exchanges:
            return None
        
        try:
            if self.settings.PAPER_TRADING:
                # Return simulated balance
                return {
                    'USDT': {'free': 10000.0, 'used': 0.0, 'total': 10000.0},
                    'BTC': {'free': 0.0, 'used': 0.0, 'total': 0.0}
                }
            
            exchange_obj = self.exchanges[exchange_name]
            balance = await exchange_obj.fetch_balance()
            return balance
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None
    
    async def get_order_book(self, symbol: str, limit: int = 20, exchange: Optional[str] = None) -> Optional[dict]:
        """Get order book for a symbol"""
        exchange_name = exchange or self.default_exchange
        
        if exchange_name not in self.exchanges:
            return None
        
        try:
            exchange_obj = self.exchanges[exchange_name]
            order_book = await exchange_obj.fetch_order_book(symbol, limit)
            return order_book
        except Exception as e:
            logger.error(f"Error getting order book for {symbol}: {e}")
            return None
    
    async def get_trades(self, symbol: str, limit: int = 50, exchange: Optional[str] = None) -> Optional[List[dict]]:
        """Get recent trades for a symbol"""
        exchange_name = exchange or self.default_exchange
        
        if exchange_name not in self.exchanges:
            return None
        
        try:
            exchange_obj = self.exchanges[exchange_name]
            trades = await exchange_obj.fetch_trades(symbol, limit=limit)
            return trades
        except Exception as e:
            logger.error(f"Error getting trades for {symbol}: {e}")
            return None
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 100,
        exchange: Optional[str] = None
    ) -> Optional[List[List]]:
        """Get OHLCV data for a symbol"""
        exchange_name = exchange or self.default_exchange
        
        if exchange_name not in self.exchanges:
            return None
        
        try:
            exchange_obj = self.exchanges[exchange_name]
            ohlcv = await exchange_obj.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error getting OHLCV for {symbol}: {e}")
            return None
    
    async def cancel_order(self, order_id: str, symbol: str, exchange: Optional[str] = None) -> Optional[dict]:
        """Cancel an order"""
        exchange_name = exchange or self.default_exchange
        
        if exchange_name not in self.exchanges:
            return None
        
        try:
            if self.settings.PAPER_TRADING:
                # Simulate order cancellation
                return {
                    'id': order_id,
                    'status': 'canceled',
                    'simulated': True
                }
            
            exchange_obj = self.exchanges[exchange_name]
            result = await exchange_obj.cancel_order(order_id, symbol)
            return result
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {e}")
            return None
    
    async def get_open_orders(self, symbol: Optional[str] = None, exchange: Optional[str] = None) -> Optional[List[dict]]:
        """Get open orders"""
        exchange_name = exchange or self.default_exchange
        
        if exchange_name not in self.exchanges:
            return None
        
        try:
            if self.settings.PAPER_TRADING:
                # Return empty list for paper trading
                return []
            
            exchange_obj = self.exchanges[exchange_name]
            orders = await exchange_obj.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return None
    
    def get_available_exchanges(self) -> List[str]:
        """Get list of available exchanges"""
        return list(self.exchanges.keys())
    
    def is_exchange_available(self, exchange_name: str) -> bool:
        """Check if exchange is available"""
        return exchange_name in self.exchanges