"""Configuration management for the trading bot"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    SECRET_KEY: str = "your-secret-key-here"
    
    # Database
    DATABASE_URL: str = "sqlite:///./trading_bot.db"
    
    # Exchange Configuration
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    BINANCE_SANDBOX: bool = True
    
    # TradingView
    TRADINGVIEW_WEBHOOK_SECRET: str = "your-webhook-secret"
    
    # Risk Management
    MAX_POSITION_SIZE: float = 0.1
    MAX_DAILY_LOSS: float = 0.05
    STOP_LOSS_PERCENTAGE: float = 0.02
    TAKE_PROFIT_PERCENTAGE: float = 0.04
    
    # AI/ML Settings
    ML_MODEL_RETRAIN_INTERVAL: int = 24
    LOOKBACK_PERIOD: int = 100
    FEATURE_ENGINEERING_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/trading_bot.log"
    
    # Trading
    PAPER_TRADING: bool = True
    DEFAULT_EXCHANGE: str = "binance"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()