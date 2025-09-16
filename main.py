"""
TradingView AI Trading Bot
A comprehensive AI-powered trading bot with TradingView integration
"""

import asyncio
import uvicorn
from loguru import logger
from src.trading_bot.core.config import get_settings
from src.trading_bot.api.main import create_app
from src.trading_bot.core.bot import TradingBot


async def main():
    """Main entry point for the trading bot"""
    settings = get_settings()
    
    # Configure logging
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        rotation="1 day",
        retention="30 days"
    )
    
    logger.info("Starting TradingView AI Trading Bot v2.0")
    
    # Initialize the trading bot
    bot = TradingBot()
    await bot.initialize()
    
    # Create FastAPI app
    app = create_app(bot)
    
    # Start the bot in background
    bot_task = asyncio.create_task(bot.start())
    
    # Start the API server
    config = uvicorn.Config(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down trading bot...")
        await bot.stop()
        bot_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())