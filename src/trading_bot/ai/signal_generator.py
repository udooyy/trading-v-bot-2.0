"""AI signal generation using machine learning"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from loguru import logger
import ta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


class AISignalGenerator:
    """AI-powered signal generation"""
    
    def __init__(self):
        self.models: Dict[str, RandomForestClassifier] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.is_trained = False
        
    async def initialize(self):
        """Initialize AI signal generator"""
        logger.info("Initializing AI signal generator...")
        # Pre-train models with sample data or load existing models
        await self._load_or_train_models()
        
    async def _load_or_train_models(self):
        """Load existing models or train new ones"""
        # For now, we'll create a simple model
        # In production, you'd load pre-trained models or train on historical data
        self.models['default'] = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.scalers['default'] = StandardScaler()
        
        # Create sample training data for demonstration
        sample_features = np.random.rand(1000, 20)
        sample_labels = np.random.choice([0, 1, 2], 1000)  # 0=hold, 1=buy, 2=sell
        
        # Fit scaler and model
        sample_features_scaled = self.scalers['default'].fit_transform(sample_features)
        self.models['default'].fit(sample_features_scaled, sample_labels)
        
        self.is_trained = True
        logger.info("AI models initialized")
    
    async def generate_signals(self, market_data: Dict[str, pd.DataFrame] = None) -> List[dict]:
        """Generate trading signals using AI"""
        signals = []
        
        if not self.is_trained or not market_data:
            return signals
        
        for symbol, data in market_data.items():
            try:
                signal = await self._analyze_symbol(symbol, data)
                if signal:
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
        
        return signals
    
    async def _analyze_symbol(self, symbol: str, data: pd.DataFrame) -> Optional[dict]:
        """Analyze a single symbol and generate signal"""
        if len(data) < 50:  # Need enough data for features
            return None
        
        # Extract features
        features = self._extract_features(data)
        if features is None:
            return None
        
        # Scale features
        features_scaled = self.scalers['default'].transform([features])
        
        # Get prediction
        prediction = self.models['default'].predict(features_scaled)[0]
        confidence = max(self.models['default'].predict_proba(features_scaled)[0])
        
        # Convert prediction to signal
        if prediction == 1 and confidence > 0.7:  # Buy signal
            return {
                'symbol': symbol,
                'action': 'buy',
                'confidence': confidence,
                'strategy': 'ai_ml',
                'features': {
                    'rsi': features[0],
                    'macd': features[1],
                    'bb_position': features[2]
                }
            }
        elif prediction == 2 and confidence > 0.7:  # Sell signal
            return {
                'symbol': symbol,
                'action': 'sell',
                'confidence': confidence,
                'strategy': 'ai_ml',
                'features': {
                    'rsi': features[0],
                    'macd': features[1],
                    'bb_position': features[2]
                }
            }
        
        return None
    
    def _extract_features(self, data: pd.DataFrame) -> Optional[List[float]]:
        """Extract technical features from market data"""
        try:
            # Ensure required columns exist
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required_columns):
                return None
            
            # Calculate technical indicators
            features = []
            
            # RSI
            rsi = ta.momentum.RSIIndicator(data['close']).rsi().iloc[-1]
            features.append(rsi if not np.isnan(rsi) else 50.0)
            
            # MACD
            macd = ta.trend.MACD(data['close'])
            macd_diff = macd.macd_diff().iloc[-1]
            features.append(macd_diff if not np.isnan(macd_diff) else 0.0)
            
            # Bollinger Bands position
            bb = ta.volatility.BollingerBands(data['close'])
            bb_high = bb.bollinger_hband().iloc[-1]
            bb_low = bb.bollinger_lband().iloc[-1]
            current_price = data['close'].iloc[-1]
            bb_position = (current_price - bb_low) / (bb_high - bb_low)
            features.append(bb_position if not np.isnan(bb_position) else 0.5)
            
            # Moving averages
            sma_20 = data['close'].rolling(20).mean().iloc[-1]
            sma_50 = data['close'].rolling(50).mean().iloc[-1]
            ma_ratio = current_price / sma_20 if not np.isnan(sma_20) else 1.0
            features.append(ma_ratio)
            
            # Volume indicators
            volume_sma = data['volume'].rolling(20).mean().iloc[-1]
            volume_ratio = data['volume'].iloc[-1] / volume_sma if volume_sma > 0 else 1.0
            features.append(volume_ratio if not np.isnan(volume_ratio) else 1.0)
            
            # Price change features
            price_change_1d = (current_price - data['close'].iloc[-2]) / data['close'].iloc[-2]
            price_change_5d = (current_price - data['close'].iloc[-6]) / data['close'].iloc[-6]
            features.extend([price_change_1d, price_change_5d])
            
            # Volatility
            volatility = data['close'].pct_change().rolling(20).std().iloc[-1]
            features.append(volatility if not np.isnan(volatility) else 0.02)
            
            # Add more features to reach 20 total
            # Support/Resistance levels
            recent_high = data['high'].rolling(20).max().iloc[-1]
            recent_low = data['low'].rolling(20).min().iloc[-1]
            high_distance = (recent_high - current_price) / current_price
            low_distance = (current_price - recent_low) / current_price
            features.extend([high_distance, low_distance])
            
            # Stochastic oscillator
            stoch = ta.momentum.StochasticOscillator(data['high'], data['low'], data['close'])
            stoch_k = stoch.stoch().iloc[-1]
            features.append(stoch_k if not np.isnan(stoch_k) else 50.0)
            
            # Williams %R
            williams_r = ta.momentum.WilliamsRIndicator(data['high'], data['low'], data['close'])
            wr = williams_r.williams_r().iloc[-1]
            features.append(wr if not np.isnan(wr) else -50.0)
            
            # Commodity Channel Index
            cci = ta.trend.CCIIndicator(data['high'], data['low'], data['close'])
            cci_value = cci.cci().iloc[-1]
            features.append(cci_value if not np.isnan(cci_value) else 0.0)
            
            # Average True Range
            atr = ta.volatility.AverageTrueRange(data['high'], data['low'], data['close'])
            atr_value = atr.average_true_range().iloc[-1]
            features.append(atr_value if not np.isnan(atr_value) else 0.01)
            
            # Money Flow Index
            mfi = ta.volume.MFIIndicator(data['high'], data['low'], data['close'], data['volume'])
            mfi_value = mfi.money_flow_index().iloc[-1]
            features.append(mfi_value if not np.isnan(mfi_value) else 50.0)
            
            # Parabolic SAR
            psar = ta.trend.PSARIndicator(data['high'], data['low'], data['close'])
            psar_value = psar.psar().iloc[-1]
            psar_signal = 1 if current_price > psar_value else 0
            features.append(psar_signal)
            
            # Ichimoku Cloud
            ichimoku = ta.trend.IchimokuIndicator(data['high'], data['low'])
            conversion_line = ichimoku.ichimoku_conversion_line().iloc[-1]
            base_line = ichimoku.ichimoku_base_line().iloc[-1]
            cloud_signal = 1 if conversion_line > base_line else 0
            features.append(cloud_signal)
            
            # Ensure we have exactly 20 features
            while len(features) < 20:
                features.append(0.0)
            
            return features[:20]
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    async def retrain_model(self, symbol: str, historical_data: pd.DataFrame, labels: List[int]):
        """Retrain model with new data"""
        try:
            features_list = []
            valid_labels = []
            
            # Extract features for each data point
            for i in range(50, len(historical_data)):
                subset = historical_data.iloc[i-50:i]
                features = self._extract_features(subset)
                if features:
                    features_list.append(features)
                    valid_labels.append(labels[i])
            
            if len(features_list) > 100:  # Need enough samples
                # Retrain model
                features_array = np.array(features_list)
                features_scaled = self.scalers['default'].fit_transform(features_array)
                self.models['default'].fit(features_scaled, valid_labels)
                
                logger.info(f"Model retrained for {symbol} with {len(features_list)} samples")
            
        except Exception as e:
            logger.error(f"Error retraining model: {e}")
    
    def get_model_info(self) -> dict:
        """Get information about trained models"""
        return {
            'is_trained': self.is_trained,
            'models': list(self.models.keys()),
            'feature_count': 20
        }