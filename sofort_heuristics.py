import time

import pygame
import torch
import random
import numpy as np
from collections import deque
import tile
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

    def get_state(self, game: Game):
        entry_point = game.board.entry
        print(game.board.cur_tile)
        # for y, row in enumerate(game.board.board):
        #     for x, elem in enumerate(row):
        #         print(f'{elem}', end="")
        #     print("\n")


        # Check which direction has danger
        danger = [0, 0, 0, 0, 0, 0]  # directions: U, UR, DR, D, DL, UL
        # 0 - no danger in that direction, 1 - dangerous direction, 2 - placed tile (unknown for now)

        closed = [(1, 1), (1, 2), (1, 6), (1, 7), (6, 1), (6, 7), (7, 1), (7, 2), (7, 3), (7, 5), (7, 6), (7, 7)]
        for y in range(9):
            for x in range(9):
                if 0 in (y, x) or 8 in (y, x):
                    closed.append((y, x))
        closed.append((4, 4))  # start

        x = game.board.x
        y = game.board.y

        if (y - 1, x) in closed:
            danger[0] = 1
        if (y + 1, x) in closed:
            danger[3] = 1
        if (y, x + 1) in closed:
            if x % 2:
                danger[1] = 1
            else:
                danger[2] = 1
        if (y, x - 1) in closed:
            if x % 2:
                danger[5] = 1
            else:
                danger[4] = 1
        if x % 2:
            if (y + 1, x + 1) in closed:
                danger[2] = 1
            if (y + 1, x - 1) in closed:
                danger[4] = 1
        else:
            if (y - 1, x + 1) in closed:
                danger[1] = 1
            if (y - 1, x - 1) in closed:
                danger[5] = 1

        return [entry_point, danger, game.board.cur_tile, game.board.swap_tile]

    def get_action(self, state):
        dangerous = True
        entry_point = state[0]
        danger = state[1]
        cur_tile = state[2]
        swap_tile = state[3]
        move = 0
        swap = 0
        counter = 0

        while dangerous:
            counter += 1
            move = random.randint(0, 5)
            new_entry = (entry_point - move * 2) % 12
            exit_point = (cur_tile.connects[new_entry] + move * 2) % 12
            if danger[exit_point // 2] == 0:
                dangerous = False
            if counter > 50:
                # swap tile
                swap = 1
                cur_tile = swap_tile
            if counter > 100:
                return [0, 0]

        final_move = [move, swap]
        return final_move


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
            state_old = agent.get_state(game)  # get old state
            final_move = agent.get_action(state_old)  # new move
            reward, game_over, score = game.play_step(final_move)  # perform move

            if game_over:
                paused = True
                game.reset()
                agent.number_of_games += 1

                if score > record:
                    record = score

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
