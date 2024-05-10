import time

import pygame
import torch
import random
import numpy as np
from collections import deque
import tile
from helper import plot
from tile import Board
from main import Game
from main import Reader

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0  # randomness parameter
        self.gamma = 0  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = None
        self.trainer = None

    def get_action(self):
        move = random.randint(0, 5)
        return [move, 0]


def train():
    plot_scores = []
    plot_average_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    board = Board()
    game = Game(board, False)
    done = True
    paused = False

    while done:
        if not paused:
            final_move = agent.get_action()  # new move
            reward, game_over, score = game.play_step(final_move)  # perform move

            if game_over:
                game.reset()
                agent.number_of_games += 1

                if score > record:
                    record = score

                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.number_of_games
                plot_average_scores.append(mean_score)
                plot(plot_scores, plot_average_scores)

                print('Game:', agent.number_of_games, 'Score:', score, 'Record:', record)
        else:
            time.sleep(0.5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                done = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = not paused


if __name__ == '__main__':
    train()

