"""Database models for the trading bot"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from ..core.config import get_settings

Base = declarative_base()


class Trade(Base):
    """Trade execution records"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # buy, sell
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    order_id = Column(String(100), unique=True, index=True)
    exchange = Column(String(20), nullable=False)
    strategy = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    pnl = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    status = Column(String(20), default="completed")  # completed, cancelled, partial
    
    def __repr__(self):
        return f"<Trade({self.symbol}, {self.side}, {self.amount}, {self.price})>"


class Position(Base):
    """Active positions"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    side = Column(String(10), nullable=False)  # long, short
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    unrealized_pnl = Column(Float, default=0.0)
    exchange = Column(String(20), nullable=False)
    strategy = Column(String(50))
    opened_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Position({self.symbol}, {self.side}, {self.quantity}, {self.entry_price})>"


class Signal(Base):
    """Trading signals received"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    action = Column(String(10), nullable=False)  # buy, sell, close
    source = Column(String(20), nullable=False)  # tradingview, ai, manual
    strategy = Column(String(50))
    price = Column(Float)
    quantity = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    confidence = Column(Float, default=1.0)
    executed = Column(Boolean, default=False)
    execution_price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(Text)  # JSON string of original signal
    
    def __repr__(self):
        return f"<Signal({self.symbol}, {self.action}, {self.source})>"


class PerformanceMetrics(Base):
    """Daily performance metrics"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    total_fees = Column(Float, default=0.0)
    portfolio_value = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<PerformanceMetrics({self.date}, PnL: {self.total_pnl})>"


class ExchangeAccount(Base):
    """Exchange account information"""
    __tablename__ = "exchange_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    exchange_name = Column(String(20), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    is_sandbox = Column(Boolean, default=True)
    total_balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    used_balance = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExchangeAccount({self.exchange_name}, {self.total_balance})>"


class AIModel(Base):
    """AI model information and performance"""
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(50), nullable=False)
    model_type = Column(String(20), nullable=False)  # classification, regression
    symbol = Column(String(20))  # specific to symbol or general
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    training_samples = Column(Integer)
    feature_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_trained = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<AIModel({self.model_name}, {self.symbol}, Acc: {self.accuracy})>"


class Configuration(Base):
    """Bot configuration settings"""
    __tablename__ = "configuration"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), nullable=False, unique=True, index=True)
    value = Column(Text)
    data_type = Column(String(20), default="string")  # string, int, float, bool, json
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Configuration({self.key}: {self.value})>"


# Database setup
def create_database_engine():
    """Create database engine"""
    settings = get_settings()
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    return engine


def create_database_session():
    """Create database session"""
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def init_database():
    """Initialize database tables"""
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)


# Database dependency for FastAPI
def get_database():
    """Database dependency for FastAPI"""
    db = create_database_session()
    try:
        yield db
    finally:
        db.close()