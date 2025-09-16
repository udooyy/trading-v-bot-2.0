import numpy as np
import random
import os
import pickle

class QLearningAgent:
    def __init__(self, state_size, action_size, alpha=0.1, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, model_path='q_agent.pkl', replay_capacity=1000, batch_size=32):
        self.state_size = state_size
        self.action_size = action_size
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount factor
        self.epsilon = epsilon  # exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.model_path = model_path
        self.q_table = {}
        self.replay_buffer = []
        self.replay_capacity = replay_capacity
        self.batch_size = batch_size
        self.load()

    def get_state_key(self, state):
        return tuple(np.round(state, 2))

    def act(self, state):
        state_key = self.get_state_key(state)
        if np.random.rand() <= self.epsilon or state_key not in self.q_table:
            return random.randrange(self.action_size)
        return np.argmax(self.q_table[state_key])

    def remember(self, state, action, reward, next_state, done):
        # Add experience to replay buffer
        if len(self.replay_buffer) >= self.replay_capacity:
            self.replay_buffer.pop(0)
        self.replay_buffer.append((state, action, reward, next_state, done))
        # Train from replay buffer
        self.replay_train()
        # Epsilon decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def replay_train(self):
        if len(self.replay_buffer) < self.batch_size:
            return
        minibatch = random.sample(self.replay_buffer, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            state_key = self.get_state_key(state)
            next_state_key = self.get_state_key(next_state)
            if state_key not in self.q_table:
                self.q_table[state_key] = np.zeros(self.action_size)
            if next_state_key not in self.q_table:
                self.q_table[next_state_key] = np.zeros(self.action_size)
            target = reward
            if not done:
                target += self.gamma * np.max(self.q_table[next_state_key])
            self.q_table[state_key][action] += self.alpha * (target - self.q_table[state_key][action])

    def save(self, versioned=True):
        path = self.model_path
        if versioned:
            # Save with timestamp for versioning
            import datetime
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            path = self.model_path.replace('.pkl', f'_{ts}.pkl')
        with open(path, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load(self, versioned=False):
        path = self.model_path
        if versioned:
            # Load the latest versioned model if available
            import glob
            files = sorted(glob.glob(self.model_path.replace('.pkl', '_*.pkl')))
            if files:
                path = files[-1]
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.q_table = pickle.load(f)
