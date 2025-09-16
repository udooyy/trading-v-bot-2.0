#!/usr/bin/env python3
"""
Demo script showing how to use the TradingView AI Trading Bot
This script demonstrates the key features and functionality
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.trading_bot.webhooks.tradingview import TradingViewWebhook
from src.trading_bot.utils.helpers import create_sample_data, calculate_technical_indicators


class TradingBotDemo:
    """Demo class for the Trading Bot"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.webhook_handler = TradingViewWebhook()
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str, description: str):
        """Print a formatted step"""
        print(f"\n🔸 {step}: {description}")
    
    def check_api_health(self):
        """Check if the API is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is running and healthy")
                return True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to API: {e}")
            print(f"💡 Make sure to start the bot first: python main.py")
            return False
    
    def demonstrate_signal_parsing(self):
        """Demonstrate TradingView signal parsing"""
        self.print_header("TradingView Signal Parsing Demo")
        
        # Create example signals
        examples = self.webhook_handler.create_example_alerts()
        
        for name, example in examples.items():
            self.print_step(f"Example: {name}", "Parsing TradingView signal")
            
            print(f"Input signal:")
            print(json.dumps(example, indent=2))
            
            parsed = self.webhook_handler.parse_tradingview_signal(example)
            if parsed:
                print(f"\nParsed signal:")
                print(json.dumps({k: v for k, v in parsed.items() if v is not None}, indent=2))
            else:
                print("❌ Failed to parse signal")
            
            print("-" * 40)
    
    def demonstrate_technical_analysis(self):
        """Demonstrate technical analysis capabilities"""
        self.print_header("Technical Analysis Demo")
        
        self.print_step("1", "Generating sample market data")
        
        # Create sample data for Bitcoin
        btc_data = create_sample_data("BTCUSDT", days=30)
        print(f"Generated {len(btc_data)} data points for BTCUSDT")
        print(f"Price range: ${btc_data['close'].min():.2f} - ${btc_data['close'].max():.2f}")
        
        self.print_step("2", "Calculating technical indicators")
        
        # Calculate technical indicators
        data_with_indicators = calculate_technical_indicators(btc_data)
        
        # Show latest values
        latest = data_with_indicators.iloc[-1]
        print(f"Latest technical indicators:")
        print(f"  Price: ${latest['close']:.2f}")
        print(f"  RSI: {latest['rsi']:.2f}")
        print(f"  MACD: {latest['macd']:.4f}")
        print(f"  Bollinger Band Position: {latest['bb_position']:.2f}")
        print(f"  Volume Ratio: {latest['volume_ratio']:.2f}")
        
        # Generate trading signal based on indicators
        self.print_step("3", "Generating trading signals")
        
        signal = None
        if latest['rsi'] > 70 and latest['bb_position'] > 0.8:
            signal = "SELL - Overbought conditions"
        elif latest['rsi'] < 30 and latest['bb_position'] < 0.2:
            signal = "BUY - Oversold conditions"
        elif latest['macd'] > latest['macd_signal'] and latest['rsi'] > 50:
            signal = "BUY - MACD bullish crossover"
        else:
            signal = "HOLD - No clear signal"
        
        print(f"Trading Signal: {signal}")
    
    def demonstrate_api_integration(self):
        """Demonstrate API integration"""
        self.print_header("API Integration Demo")
        
        if not self.check_api_health():
            return
        
        self.print_step("1", "Getting bot status")
        try:
            response = requests.get(f"{self.base_url}/api/v1/status")
            if response.status_code == 200:
                status = response.json()
                print("Bot Status:")
                for key, value in status.items():
                    print(f"  {key}: {value}")
            else:
                print(f"❌ Failed to get status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting status: {e}")
        
        self.print_step("2", "Getting portfolio information")
        try:
            response = requests.get(f"{self.base_url}/api/v1/portfolio")
            if response.status_code == 200:
                portfolio = response.json()
                print("Portfolio:")
                for key, value in portfolio.items():
                    print(f"  {key}: {value}")
            else:
                print(f"❌ Failed to get portfolio: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting portfolio: {e}")
        
        self.print_step("3", "Sending a test webhook signal")
        test_signal = {
            "symbol": "BTCUSDT",
            "action": "buy",
            "quantity": 0.01,
            "price": 50000.0,
            "strategy": "demo_test"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/webhook/tradingview",
                json=test_signal,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Webhook signal sent successfully:")
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Webhook failed: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")
    
    def demonstrate_risk_management(self):
        """Demonstrate risk management features"""
        self.print_header("Risk Management Demo")
        
        from src.trading_bot.core.risk_manager import RiskManager
        from src.trading_bot.core.config import get_settings
        
        settings = get_settings()
        risk_manager = RiskManager()
        
        self.print_step("1", "Risk Management Configuration")
        print(f"Maximum Position Size: {settings.MAX_POSITION_SIZE * 100:.1f}%")
        print(f"Maximum Daily Loss: {settings.MAX_DAILY_LOSS * 100:.1f}%")
        print(f"Default Stop Loss: {settings.STOP_LOSS_PERCENTAGE * 100:.1f}%")
        print(f"Default Take Profit: {settings.TAKE_PROFIT_PERCENTAGE * 100:.1f}%")
        
        self.print_step("2", "Signal Validation Example")
        
        # Test different signals
        test_signals = [
            {"symbol": "BTCUSDT", "action": "buy", "quantity": 0.05},  # Valid
            {"symbol": "BTCUSDT", "action": "buy", "quantity": 0.5},   # Too large
            {"symbol": "", "action": "buy", "quantity": 0.05},         # Invalid symbol
            {"symbol": "ETHUSDT", "action": "invalid", "quantity": 0.05}  # Invalid action
        ]
        
        for i, signal in enumerate(test_signals, 1):
            print(f"\nSignal {i}: {signal}")
            
            # This would normally be async
            import asyncio
            is_valid = asyncio.run(risk_manager.validate_trade(signal))
            print(f"Validation result: {'✅ PASS' if is_valid else '❌ FAIL'}")
    
    def run_full_demo(self):
        """Run the complete demo"""
        print("🚀 TradingView AI Trading Bot - Feature Demonstration")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run all demonstrations
            self.demonstrate_signal_parsing()
            self.demonstrate_technical_analysis()
            self.demonstrate_risk_management()
            self.demonstrate_api_integration()
            
            self.print_header("Demo Completed Successfully!")
            print("🎉 All features demonstrated successfully!")
            print("\n📚 Next Steps:")
            print("1. Configure your .env file with real API keys")
            print("2. Set up TradingView alerts to send to your webhook")
            print("3. Monitor the bot's performance via the web dashboard")
            print("4. Review logs for detailed trading activity")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Demo interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    demo = TradingBotDemo()
    demo.run_full_demo()