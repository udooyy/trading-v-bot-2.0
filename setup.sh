#!/bin/bash
# Quick setup script for the TradingView AI Trading Bot

echo "🚀 TradingView AI Trading Bot - Quick Setup"
echo "==========================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.12 or higher."
    exit 1
fi

echo "✅ Python is available"

# Check Python version
python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env file with your API keys and settings"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs
echo "✅ Created logs directory"

# Run basic tests
echo "🧪 Running basic tests..."
python -c "
import sys
sys.path.append('.')
from src.trading_bot.core.config import get_settings
from src.trading_bot.webhooks.tradingview import TradingViewWebhook
print('✅ All imports successful')
"

if [ $? -eq 0 ]; then
    echo "✅ Basic tests passed"
else
    echo "❌ Basic tests failed"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your configuration:"
echo "   - Add exchange API keys (optional for paper trading)"
echo "   - Set TradingView webhook secret"
echo "   - Configure risk management parameters"
echo ""
echo "2. Start the trading bot:"
echo "   python main.py"
echo ""
echo "3. Access the web interface:"
echo "   http://localhost:8000"
echo ""
echo "4. View API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Test with demo script:"
echo "   python demo.py"
echo ""
echo "📖 For more information, see the README.md file"