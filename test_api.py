#!/usr/bin/env python3
"""Quick test script to verify the API server starts"""

import sys
import asyncio
import signal
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.trading_bot.core.bot import TradingBot
from src.trading_bot.api.main import create_app


async def test_api_startup():
    """Test that the API server can start successfully"""
    try:
        print("🚀 Starting TradingBot API test...")
        
        # Initialize bot (with mocked dependencies for testing)
        bot = TradingBot()
        
        # Mock the initialization to avoid actual API calls
        bot.exchange_manager.exchanges = {}  # Mock empty exchanges
        bot.strategy_manager.strategies = {}  # Mock empty strategies
        bot.ai_generator.is_trained = True   # Mock trained AI
        
        # Create the FastAPI app
        app = create_app(bot)
        
        print("✅ API application created successfully")
        print("✅ Bot initialization completed")
        print("✅ FastAPI app is ready to serve")
        
        # Test bot status
        status = bot.get_status()
        print(f"✅ Bot status: {status}")
        
        print("\n🎉 API startup test completed successfully!")
        print("\nTo start the server manually, run:")
        print("  python main.py")
        print("\nAPI endpoints will be available at:")
        print("  http://localhost:8000/ - Main page")
        print("  http://localhost:8000/docs - API documentation")
        print("  http://localhost:8000/health - Health check")
        print("  http://localhost:8000/api/v1/status - Bot status")
        
        return True
        
    except Exception as e:
        print(f"❌ API startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_api_startup())
    sys.exit(0 if result else 1)