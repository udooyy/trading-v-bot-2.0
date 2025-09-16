"""Strategy management system"""

from typing import Dict, List, Optional
from abc import ABC, abstractmethod
import pandas as pd
from loguru import logger


class BaseStrategy(ABC):
    """Base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        
    @abstractmethod
    async def analyze(self, market_data: pd.DataFrame) -> Optional[dict]:
        """Analyze market data and return trading signal"""
        pass
    
    @abstractmethod
    async def validate_signal(self, signal: dict) -> bool:
        """Validate a trading signal"""
        pass


class AISignalStrategy(BaseStrategy):
    """Strategy that processes AI-generated signals"""
    
    def __init__(self):
        super().__init__("ai_signal")
        
    async def analyze(self, market_data: pd.DataFrame) -> Optional[dict]:
        """Analyze market data using AI"""
        # This would integrate with the AI signal generator
        return None
    
    async def validate_signal(self, signal: dict) -> bool:
        """Validate AI signal"""
        required_fields = ['symbol', 'action', 'confidence']
        return all(field in signal for field in required_fields)


class TechnicalAnalysisStrategy(BaseStrategy):
    """Strategy based on technical indicators"""
    
    def __init__(self):
        super().__init__("technical_analysis")
        
    async def analyze(self, market_data: pd.DataFrame) -> Optional[dict]:
        """Analyze using technical indicators"""
        if len(market_data) < 20:
            return None
            
        # Simple moving average crossover example
        market_data['SMA_10'] = market_data['close'].rolling(10).mean()
        market_data['SMA_20'] = market_data['close'].rolling(20).mean()
        
        latest = market_data.iloc[-1]
        previous = market_data.iloc[-2]
        
        # Check for golden cross (SMA10 crosses above SMA20)
        if (latest['SMA_10'] > latest['SMA_20'] and 
            previous['SMA_10'] <= previous['SMA_20']):
            return {
                'symbol': 'BTC/USDT',  # This should come from the data
                'action': 'buy',
                'confidence': 0.7,
                'strategy': self.name,
                'indicators': {
                    'sma_10': latest['SMA_10'],
                    'sma_20': latest['SMA_20']
                }
            }
        
        # Check for death cross (SMA10 crosses below SMA20)
        elif (latest['SMA_10'] < latest['SMA_20'] and 
              previous['SMA_10'] >= previous['SMA_20']):
            return {
                'symbol': 'BTC/USDT',
                'action': 'sell',
                'confidence': 0.7,
                'strategy': self.name,
                'indicators': {
                    'sma_10': latest['SMA_10'],
                    'sma_20': latest['SMA_20']
                }
            }
        
        return None
    
    async def validate_signal(self, signal: dict) -> bool:
        """Validate technical analysis signal"""
        return signal.get('confidence', 0) > 0.5


class StrategyManager:
    """Manages multiple trading strategies"""
    
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.enabled_strategies: List[str] = []
        
    async def initialize(self):
        """Initialize strategy manager"""
        # Register built-in strategies
        self.register_strategy(AISignalStrategy())
        self.register_strategy(TechnicalAnalysisStrategy())
        
        # Enable default strategies
        self.enable_strategy("ai_signal")
        self.enable_strategy("technical_analysis")
        
        logger.info(f"Strategy manager initialized with {len(self.strategies)} strategies")
    
    def register_strategy(self, strategy: BaseStrategy):
        """Register a new strategy"""
        self.strategies[strategy.name] = strategy
        logger.info(f"Registered strategy: {strategy.name}")
    
    def enable_strategy(self, strategy_name: str):
        """Enable a strategy"""
        if strategy_name in self.strategies and strategy_name not in self.enabled_strategies:
            self.enabled_strategies.append(strategy_name)
            self.strategies[strategy_name].enabled = True
            logger.info(f"Enabled strategy: {strategy_name}")
    
    def disable_strategy(self, strategy_name: str):
        """Disable a strategy"""
        if strategy_name in self.enabled_strategies:
            self.enabled_strategies.remove(strategy_name)
            self.strategies[strategy_name].enabled = False
            logger.info(f"Disabled strategy: {strategy_name}")
    
    async def generate_signals(self, market_data: Dict[str, pd.DataFrame]) -> List[dict]:
        """Generate signals from all enabled strategies"""
        signals = []
        
        for strategy_name in self.enabled_strategies:
            strategy = self.strategies[strategy_name]
            
            for symbol, data in market_data.items():
                try:
                    signal = await strategy.analyze(data)
                    if signal and await strategy.validate_signal(signal):
                        signals.append(signal)
                except Exception as e:
                    logger.error(f"Error in strategy {strategy_name}: {e}")
        
        return signals
    
    def get_strategy_status(self) -> Dict[str, dict]:
        """Get status of all strategies"""
        return {
            name: {
                'enabled': strategy.enabled,
                'name': strategy.name
            }
            for name, strategy in self.strategies.items()
        }