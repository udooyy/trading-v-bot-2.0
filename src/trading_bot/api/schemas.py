"""Pydantic schemas for API request/response models"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class TradeAction(str, Enum):
    """Trade action types"""
    BUY = "buy"
    SELL = "sell"
    LONG = "long"
    SHORT = "short"
    CLOSE = "close"


class TradeSide(str, Enum):
    """Trade side types"""
    LONG = "long"
    SHORT = "short"


# Request schemas
class TradeRequest(BaseModel):
    """Manual trade request"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    action: TradeAction = Field(..., description="Trade action")
    quantity: float = Field(..., gt=0, description="Trade quantity")
    price: Optional[float] = Field(None, description="Limit price (optional for market orders)")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "action": "buy",
                "quantity": 0.1,
                "stop_loss": 45000,
                "take_profit": 55000
            }
        }


class ClosePositionRequest(BaseModel):
    """Close position request"""
    symbol: str = Field(..., description="Symbol to close position for")
    quantity: Optional[float] = Field(None, description="Partial quantity to close (optional)")


class AnalysisRequest(BaseModel):
    """Symbol analysis request"""
    symbol: str = Field(..., description="Symbol to analyze")
    timeframe: Optional[str] = Field("1h", description="Analysis timeframe")
    indicators: Optional[List[str]] = Field(None, description="Specific indicators to include")


# Response schemas
class TradeResponse(BaseModel):
    """Trade execution response"""
    success: bool
    message: str
    order_id: Optional[str] = None
    execution_price: Optional[float] = None


class PositionResponse(BaseModel):
    """Position information response"""
    symbol: str
    side: TradeSide
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: datetime


class PortfolioResponse(BaseModel):
    """Portfolio overview response"""
    total_value: float
    cash_balance: float
    positions_count: int
    daily_pnl: float
    daily_pnl_percent: float


class PerformanceResponse(BaseModel):
    """Performance metrics response"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    sharpe_ratio: float
    max_drawdown: float


class AnalysisResponse(BaseModel):
    """Symbol analysis response"""
    symbol: str
    signal: str  # buy, sell, hold
    confidence: float
    indicators: Dict[str, float]
    prediction: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BotStatusResponse(BaseModel):
    """Bot status response"""
    is_running: bool
    active_positions: int
    portfolio_value: float
    daily_pnl: float
    uptime: str


class WebhookResponse(BaseModel):
    """Webhook processing response"""
    success: bool
    message: str
    signal: Optional[Dict[str, Any]] = None


class StrategyStatusResponse(BaseModel):
    """Strategy status response"""
    name: str
    enabled: bool
    description: Optional[str] = None


class ExchangeStatusResponse(BaseModel):
    """Exchange status response"""
    name: str
    available: bool
    balance: Optional[float] = None
    is_sandbox: bool


class SignalRequest(BaseModel):
    """Signal submission request"""
    symbol: str
    action: TradeAction
    quantity: Optional[float] = None
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy: Optional[str] = "manual"
    confidence: Optional[float] = 1.0
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "ETHUSDT",
                "action": "buy",
                "quantity": 0.5,
                "price": 2500.0,
                "stop_loss": 2400.0,
                "take_profit": 2700.0,
                "strategy": "breakout",
                "confidence": 0.85
            }
        }


class BacktestRequest(BaseModel):
    """Backtesting request"""
    symbol: str
    strategy: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000.0
    parameters: Optional[Dict[str, Any]] = None


class BacktestResponse(BaseModel):
    """Backtesting results response"""
    symbol: str
    strategy: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    profit_factor: float


class AlertRequest(BaseModel):
    """Alert configuration request"""
    symbol: str
    condition: str  # price_above, price_below, rsi_overbought, etc.
    value: float
    enabled: bool = True


class AlertResponse(BaseModel):
    """Alert response"""
    id: int
    symbol: str
    condition: str
    value: float
    enabled: bool
    triggered: bool
    created_at: datetime


class ConfigurationResponse(BaseModel):
    """Configuration response"""
    paper_trading: bool
    max_position_size: float
    max_daily_loss: float
    default_exchange: str
    strategies: Dict[str, Dict[str, Any]]


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)