import torch
import random
import numpy as np
import matplotlib.pyplot as plt
from IPython import display
from shooterAI import SpaceshipAI

from collections import deque
from model import Linear_Q_net, QTrainer

MAX_MEMORY = 400000
BATCH_SIZE = 2000

LR = 0.1

plt.ion()


def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Train')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))


class Agent:
    def __init__(self):
        self.num_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discont rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_Q_net(12, 4, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        state = game.get_states()
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves , tradeoff / exploitation
        self.epsilon = 100 - self.num_games
        final_move = [0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():
    plot_scores = []
    plot_mean = []
    last_10_score = deque(maxlen=10)
    record = 0

    agent = Agent()
    game = SpaceshipAI()
    while True:
        stateold = agent.get_state(game)
        final_move = agent.get_action(stateold)
        reward, done, score = game.play_step(final_move)
        statenew = agent.get_state(game)
        agent.train_short_memory(stateold, final_move, reward, statenew, done)
        agent.remember(stateold, final_move, reward, statenew, done)

        if done:
            # Train long memory , plot results
            game.reset_game()
            agent.num_games += 1
            agent.train_long_memory()
            if score > record:
                record = score
                agent.model.save_model()
            print(agent.num_games, ' ', score, ' ', record)
            plot_scores.append(score)
            last_10_score.append(score)
            mean_score = np.sum(last_10_score) / len(last_10_score)
            plot_mean.append(mean_score)
            plot(plot_scores, plot_mean)


if __name__ == '__main__':
    train()
