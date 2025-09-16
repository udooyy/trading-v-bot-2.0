# TradingView Alert Examples

This file contains example alert configurations for TradingView to work with the AI Trading Bot.

## Basic Alert Configuration

### 1. Simple Buy Signal
```
Webhook URL: http://your-server:8000/webhook/tradingview
Message:
{
  "symbol": "{{ticker}}",
  "action": "buy",
  "price": {{close}},
  "quantity": 0.1
}
```

### 2. Comprehensive Trading Signal
```
Webhook URL: http://your-server:8000/webhook/tradingview
Message:
{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}",
  "quantity": 0.05,
  "price": {{close}},
  "stop_loss": {{strategy.order.stop_loss}},
  "take_profit": {{strategy.order.take_profit}},
  "strategy": "my_strategy",
  "timeframe": "{{interval}}",
  "confidence": 0.85
}
```

### 3. Text-based Alert (Parsed automatically)
```
Webhook URL: http://your-server:8000/webhook/tradingview
Message:
Symbol: {{ticker}}
Action: buy
Entry: {{close}}
Stop Loss: {{low}}
Take Profit: {{high}}
Strategy: RSI Divergence
Timeframe: {{interval}}
```

### 4. Close Position Signal
```
Webhook URL: http://your-server:8000/webhook/tradingview
Message:
{
  "symbol": "{{ticker}}",
  "action": "close",
  "strategy": "manual_exit"
}
```

## Pine Script Example

Here's a simple Pine Script that can send alerts to your bot:

```pinescript
//@version=5
strategy("AI Trading Bot Strategy", overlay=true)

// Strategy parameters
rsi_length = input.int(14, "RSI Length")
rsi_overbought = input.int(70, "RSI Overbought")
rsi_oversold = input.int(30, "RSI Oversold")

// Calculate RSI
rsi = ta.rsi(close, rsi_length)

// Entry conditions
long_condition = ta.crossover(rsi, rsi_oversold)
short_condition = ta.crossunder(rsi, rsi_overbought)

// Execute trades
if long_condition
    strategy.entry("Long", strategy.long)
    alert('{"symbol": "' + syminfo.ticker + '", "action": "buy", "price": ' + str.tostring(close) + ', "quantity": 0.1, "strategy": "rsi_strategy"}', alert.freq_once_per_bar)

if short_condition
    strategy.entry("Short", strategy.short)
    alert('{"symbol": "' + syminfo.ticker + '", "action": "sell", "price": ' + str.tostring(close) + ', "quantity": 0.1, "strategy": "rsi_strategy"}', alert.freq_once_per_bar)

// Plot RSI
plot(rsi, "RSI", color=color.purple)
hline(rsi_overbought, "Overbought", color=color.red)
hline(rsi_oversold, "Oversold", color=color.green)
```

## Alert Setup Instructions

1. **Open TradingView** and go to the chart you want to monitor
2. **Click the Alert button** (clock icon) or press Alt+A
3. **Configure the alert**:
   - Condition: Choose your indicator or strategy
   - Options: Set frequency (Once Per Bar Close recommended)
   - Actions: Enable "Webhook URL"
   - Webhook URL: `http://your-server:8000/webhook/tradingview`
   - Message: Use one of the examples above
4. **Test the alert** by triggering the condition manually
5. **Monitor the bot logs** to ensure signals are received and processed

## Security Notes

- Use HTTPS in production: `https://your-server.com/webhook/tradingview`
- Configure `TRADINGVIEW_WEBHOOK_SECRET` in your .env file
- Consider IP whitelisting for additional security
- Monitor webhook calls in your bot logs

## Troubleshooting

### Alert not triggering trades
1. Check bot logs for error messages
2. Verify webhook URL is accessible
3. Ensure JSON format is valid
4. Check risk management settings

### Invalid signal format
1. Verify required fields: `symbol`, `action`
2. Check symbol format (should match exchange format)
3. Ensure action is one of: buy, sell, long, short, close

### Risk management rejecting trades
1. Check position size limits
2. Verify daily loss limits not exceeded
3. Review stop loss/take profit settings
4. Ensure sufficient account balance