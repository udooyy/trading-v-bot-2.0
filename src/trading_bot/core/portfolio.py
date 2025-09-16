"""Portfolio management"""

from typing import Dict, List
from datetime import datetime
from loguru import logger


class Portfolio:
    """Portfolio tracking and management"""
    
    def __init__(self):
        self.positions: Dict[str, dict] = {}
        self.cash_balance = 10000.0  # Starting balance
        self.total_value = self.cash_balance
        self.daily_start_value = self.cash_balance
        
    async def initialize(self):
        """Initialize portfolio"""
        logger.info("Initializing portfolio...")
        # Load existing positions from database
        # Implementation would connect to database
        
    async def update(self):
        """Update portfolio values"""
        # Update position values based on current market prices
        # Implementation would fetch current prices and calculate P&L
        pass
    
    def add_position(self, symbol: str, quantity: float, price: float, side: str):
        """Add a position to the portfolio"""
        if symbol in self.positions:
            # Update existing position
            existing = self.positions[symbol]
            total_quantity = existing['quantity'] + quantity
            avg_price = ((existing['quantity'] * existing['price']) + 
                        (quantity * price)) / total_quantity
            
            self.positions[symbol] = {
                'quantity': total_quantity,
                'price': avg_price,
                'side': side,
                'timestamp': datetime.utcnow()
            }
        else:
            # New position
            self.positions[symbol] = {
                'quantity': quantity,
                'price': price,
                'side': side,
                'timestamp': datetime.utcnow()
            }
    
    def remove_position(self, symbol: str, quantity: float = None):
        """Remove or reduce a position"""
        if symbol in self.positions:
            if quantity is None or quantity >= self.positions[symbol]['quantity']:
                # Remove entire position
                del self.positions[symbol]
            else:
                # Reduce position
                self.positions[symbol]['quantity'] -= quantity
    
    def get_position(self, symbol: str) -> dict:
        """Get position details"""
        return self.positions.get(symbol)
    
    def get_total_value(self) -> float:
        """Get total portfolio value"""
        return self.total_value
    
    def get_daily_pnl(self) -> float:
        """Get daily profit/loss"""
        return self.total_value - self.daily_start_value
    
    def get_daily_pnl_percentage(self) -> float:
        """Get daily P&L as percentage"""
        if self.daily_start_value == 0:
            return 0.0
        return ((self.total_value - self.daily_start_value) / self.daily_start_value) * 100
    
    def get_positions_summary(self) -> List[dict]:
        """Get summary of all positions"""
        return [
            {
                'symbol': symbol,
                'quantity': pos['quantity'],
                'price': pos['price'],
                'side': pos['side'],
                'timestamp': pos['timestamp']
            }
            for symbol, pos in self.positions.items()
        ]