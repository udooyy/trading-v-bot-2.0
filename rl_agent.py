import numpy as np
import random
import os
import pickle
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import gymnasium as gym

class PPOAgent:
    def __init__(self, state_size, action_size, alpha=0.001, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, model_path='ppo_agent.zip', replay_capacity=10000, batch_size=64):
        self.state_size = state_size
        self.action_size = action_size
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.model_path = model_path
        self.replay_buffer = []
        self.replay_capacity = replay_capacity
        self.batch_size = batch_size
        
        # Create a simple gym env wrapper for trading
        class TradingEnv(gym.Env):
            def __init__(self):
                self.action_space = gym.spaces.Discrete(action_size)
                self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(state_size,))
            def step(self, action):
                # Placeholder: implement reward, next_state, done based on trading logic
                reward = 0  # Replace with actual reward calculation
                next_state = np.zeros(state_size)  # Replace with actual next state
                done = False  # Replace with actual done condition
                return next_state, reward, done, {}
            def reset(self):
                return np.zeros(state_size)  # Replace with initial state
        
        env = DummyVecEnv([lambda: TradingEnv()])
        self.model = PPO('MlpPolicy', env, learning_rate=alpha, gamma=gamma, verbose=1)
        self.load()

    def act(self, state):
        action, _ = self.model.predict(state)
        return action

    def remember(self, state, action, reward, next_state, done):
        # Add to replay buffer for potential custom training
        if len(self.replay_buffer) >= self.replay_capacity:
            self.replay_buffer.pop(0)
        self.replay_buffer.append((state, action, reward, next_state, done))
        # PPO handles training; call learn periodically
        if len(self.replay_buffer) % self.batch_size == 0:
            self.train()

    def train(self):
        # Train PPO on the env (integrate with backtesting)
        self.model.learn(total_timesteps=1000)  # Adjust as needed

    def save(self, versioned=True):
        path = self.model_path
        if versioned:
            import datetime
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            path = self.model_path.replace('.zip', f'_{ts}.zip')
        self.model.save(path)

    def load(self, versioned=False):
        path = self.model_path
        if versioned:
            import glob
            files = sorted(glob.glob(self.model_path.replace('.zip', '_*.zip')))
            if files:
                path = files[-1]
        if os.path.exists(path):
            self.model = PPO.load(path)
