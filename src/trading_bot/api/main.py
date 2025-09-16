"""FastAPI application for the trading bot"""

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Dict, List, Optional
import json
from loguru import logger

from ..core.bot import TradingBot
from ..webhooks.tradingview import TradingViewWebhook, SignalValidator
from ..database.models import get_database, init_database
from .schemas import *


def create_app(bot: TradingBot) -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="TradingView AI Trading Bot",
        description="AI-powered trading bot with TradingView integration",
        version="2.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize components
    webhook_handler = TradingViewWebhook()
    signal_validator = SignalValidator()
    
    # Initialize database
    init_database()
    
    @app.on_event("startup")
    async def startup_event():
        """Startup event"""
        logger.info("FastAPI application starting up")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown event"""
        logger.info("FastAPI application shutting down")
    
    # Root endpoint
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root endpoint with basic info"""
        return """
        <html>
            <head>
                <title>TradingView AI Trading Bot 2.0</title>
            </head>
            <body>
                <h1>TradingView AI Trading Bot 2.0</h1>
                <p>AI-powered trading bot with TradingView integration</p>
                <h2>API Endpoints:</h2>
                <ul>
                    <li><a href="/docs">API Documentation</a></li>
                    <li><a href="/api/v1/status">Bot Status</a></li>
                    <li><a href="/api/v1/positions">Current Positions</a></li>
                    <li><a href="/api/v1/performance">Performance Metrics</a></li>
                </ul>
                <h2>Webhook Endpoints:</h2>
                <ul>
                    <li>POST /webhook/tradingview - TradingView alerts</li>
                </ul>
            </body>
        </html>
        """
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "bot_running": bot.is_running}
    
    # Bot status
    @app.get("/api/v1/status", response_model=BotStatusResponse)
    async def get_bot_status():
        """Get bot status"""
        return bot.get_status()
    
    # Trading endpoints
    @app.post("/api/v1/trade", response_model=TradeResponse)
    async def execute_trade(trade_request: TradeRequest, background_tasks: BackgroundTasks):
        """Execute a manual trade"""
        try:
            signal = {
                'symbol': trade_request.symbol,
                'action': trade_request.action,
                'quantity': trade_request.quantity,
                'price': trade_request.price,
                'stop_loss': trade_request.stop_loss,
                'take_profit': trade_request.take_profit,
                'strategy': 'manual'
            }
            
            # Validate signal
            if not signal_validator.validate_signal(signal):
                raise HTTPException(status_code=400, detail="Invalid trade parameters")
            
            # Execute trade in background
            background_tasks.add_task(bot.process_tradingview_signal, signal)
            
            return TradeResponse(
                success=True,
                message="Trade request submitted",
                order_id=f"manual_{len(bot.active_positions)}"
            )
            
        except Exception as e:
            logger.error(f"Error executing manual trade: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/positions", response_model=List[PositionResponse])
    async def get_positions():
        """Get current positions"""
        try:
            positions = []
            for symbol, position in bot.active_positions.items():
                positions.append(PositionResponse(
                    symbol=symbol,
                    side=position.side,
                    quantity=position.quantity,
                    entry_price=position.entry_price,
                    current_price=position.current_price or position.entry_price,
                    unrealized_pnl=0.0,  # Calculate actual PnL
                    stop_loss=position.stop_loss,
                    take_profit=position.take_profit,
                    opened_at=position.timestamp
                ))
            return positions
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/close-position")
    async def close_position(close_request: ClosePositionRequest, background_tasks: BackgroundTasks):
        """Close a specific position"""
        try:
            if close_request.symbol not in bot.active_positions:
                raise HTTPException(status_code=404, detail="Position not found")
            
            # Close position in background
            background_tasks.add_task(bot._close_position, close_request.symbol)
            
            return {"success": True, "message": f"Position {close_request.symbol} closing"}
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Portfolio endpoints
    @app.get("/api/v1/portfolio", response_model=PortfolioResponse)
    async def get_portfolio():
        """Get portfolio overview"""
        try:
            return PortfolioResponse(
                total_value=bot.portfolio.get_total_value(),
                cash_balance=bot.portfolio.cash_balance,
                positions_count=len(bot.active_positions),
                daily_pnl=bot.portfolio.get_daily_pnl(),
                daily_pnl_percent=bot.portfolio.get_daily_pnl_percentage()
            )
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/performance", response_model=PerformanceResponse)
    async def get_performance():
        """Get performance metrics"""
        try:
            # This would typically fetch from database
            return PerformanceResponse(
                total_trades=len(bot.active_positions),
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=bot.portfolio.get_daily_pnl(),
                sharpe_ratio=0.0,
                max_drawdown=0.0
            )
        except Exception as e:
            logger.error(f"Error getting performance: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # AI/ML endpoints
    @app.post("/api/v1/analyze", response_model=AnalysisResponse)
    async def analyze_symbol(analysis_request: AnalysisRequest):
        """Perform AI analysis on a symbol"""
        try:
            # This would integrate with the AI signal generator
            return AnalysisResponse(
                symbol=analysis_request.symbol,
                signal="hold",
                confidence=0.5,
                indicators={
                    "rsi": 50.0,
                    "macd": 0.0,
                    "bb_position": 0.5
                },
                prediction="neutral"
            )
        except Exception as e:
            logger.error(f"Error analyzing symbol: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Webhook endpoints
    @app.post("/webhook/tradingview")
    async def tradingview_webhook(
        request: Request,
        background_tasks: BackgroundTasks,
        webhook_secret: Optional[str] = None
    ):
        """Handle TradingView webhook"""
        try:
            # Get raw payload
            payload = await request.body()
            payload_str = payload.decode()
            
            # Validate signature if provided
            if webhook_secret:
                signature = request.headers.get("X-Webhook-Signature", "")
                if not webhook_handler.validate_webhook_signature(payload_str, signature):
                    raise HTTPException(status_code=401, detail="Invalid webhook signature")
            
            # Parse JSON payload
            try:
                webhook_data = json.loads(payload_str)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON payload")
            
            # Parse signal
            signal = webhook_handler.parse_tradingview_signal(webhook_data)
            if not signal:
                raise HTTPException(status_code=400, detail="Invalid signal format")
            
            # Validate signal
            if not signal_validator.validate_signal(signal):
                raise HTTPException(status_code=400, detail="Signal validation failed")
            
            # Sanitize signal
            signal = signal_validator.sanitize_signal(signal)
            
            # Process signal in background
            background_tasks.add_task(bot.process_tradingview_signal, signal)
            
            logger.info(f"TradingView webhook processed: {signal['symbol']} {signal['action']}")
            
            return {
                "success": True,
                "message": "Signal received and queued for processing",
                "signal": {
                    "symbol": signal['symbol'],
                    "action": signal['action'],
                    "strategy": signal.get('strategy', 'tradingview')
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing TradingView webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Configuration endpoints
    @app.get("/api/v1/config")
    async def get_config():
        """Get bot configuration"""
        try:
            return {
                "paper_trading": bot.settings.PAPER_TRADING,
                "max_position_size": bot.settings.MAX_POSITION_SIZE,
                "max_daily_loss": bot.settings.MAX_DAILY_LOSS,
                "default_exchange": bot.settings.DEFAULT_EXCHANGE,
                "strategies": bot.strategy_manager.get_strategy_status()
            }
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/strategy/{strategy_name}/enable")
    async def enable_strategy(strategy_name: str):
        """Enable a trading strategy"""
        try:
            bot.strategy_manager.enable_strategy(strategy_name)
            return {"success": True, "message": f"Strategy {strategy_name} enabled"}
        except Exception as e:
            logger.error(f"Error enabling strategy: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/strategy/{strategy_name}/disable")
    async def disable_strategy(strategy_name: str):
        """Disable a trading strategy"""
        try:
            bot.strategy_manager.disable_strategy(strategy_name)
            return {"success": True, "message": f"Strategy {strategy_name} disabled"}
        except Exception as e:
            logger.error(f"Error disabling strategy: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Emergency stop
    @app.post("/api/v1/emergency-stop")
    async def emergency_stop(background_tasks: BackgroundTasks):
        """Emergency stop - close all positions and halt trading"""
        try:
            background_tasks.add_task(bot._emergency_stop)
            return {"success": True, "message": "Emergency stop activated"}
        except Exception as e:
            logger.error(f"Error activating emergency stop: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app