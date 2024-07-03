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
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.0001


class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0  # randomness parameter
        self.gamma = 0.9  # discount rate, smaller than 1
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(73, 100, 12)
        self.trainer = QTrainer(self.model, learning_rate=LR, gamma=self.gamma)

    def get_state(self, game: Game):
        entry_point = game.board.entry
        # print(game.board.cur_tile)

        closed = [(1, 1), (1, 2), (1, 6), (1, 7), (6, 1), (6, 7), (7, 1), (7, 2), (7, 3), (7, 5), (7, 6), (7, 7)]
        for y in range(9):
            for x in range(9):
                if 0 in (y, x) or 8 in (y, x):
                    closed.append((y, x))
        closed.append((4, 4))  # start

        x = game.board.x
        y = game.board.y

        # Need info for every each one of 12 paths - danger or not, if not, how much plates till out, where out
        path_info = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                     [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

        def find_depth(y1, x1, depth, direction):
            # print(f'{y1} {x1} and {y} {x} on depth {depth} and looking at path {direction}')
            if y1 == y and x1 == x:
                # print(f'{y1} {x1} and {y} {x} and it looped')
                return [-1, -1, -1, -1]
            if game.board.board[y1][x1].kind == tile.Tile.OPEN:
                # print("current tile is open")
                return [0, depth, y1, x1]
            elif game.board.board[y1][x1].kind == tile.Tile.CLOSED or game.board.board[y1][x1].kind == tile.Tile.START:
                # print("current tile is closed or start, aka danger")
                return [1, depth, y1, x1]
            else:
                # print("current tile is a placed piece")
                new_direction = game.board.board[y1][x1].connects[direction]
                if new_direction == 0 or new_direction == 1:
                    y1 = y1 - 1
                elif new_direction == 2 or new_direction == 3:
                    if x1 % 2 == 0:
                        y1 = y1 - 1
                        x1 = x1 + 1
                    elif x1 % 2 == 1:
                        x1 = x1 + 1
                elif new_direction == 4 or new_direction == 5:
                    if x1 % 2 == 0:
                        x1 = x1 + 1
                    elif x1 % 2 == 1:
                        y1 = y1 + 1
                        x1 = x1 + 1
                elif new_direction == 6 or new_direction == 7:
                    y1 = y1 + 1
                elif new_direction == 8 or new_direction == 9:
                    if x1 % 2 == 0:
                        x1 = x1 - 1
                    elif x1 % 2 == 1:
                        y1 = y1 + 1
                        x1 = x1 - 1
                elif new_direction == 10 or new_direction == 11:
                    if x1 % 2 == 0:
                        y1 = y1 - 1
                        x1 = x1 - 1
                    elif x1 % 2 == 1:
                        x1 = x1 - 1
                new_direction = tile.Tile.OPPOSITE[new_direction]
                return find_depth(y1, x1, depth + 1, new_direction)

        # print(f'Calling find depth for {y} and {x}')
        if (y, x) in closed:
            end_state = [entry_point] + [elem for sublist in path_info for elem in sublist][:48]

            for value in game.board.swap_tile.connects.values():
                end_state.append(0)

            for value in game.board.swap_tile.connects.values():
                end_state.append(value)

            return end_state

        if game.board.board[y - 1][x].kind == tile.Tile.CLOSED or game.board.board[y - 1][x].kind == tile.Tile.START:
            path_info[0][0] = 1
            path_info[1][0] = 1
        elif game.board.board[y - 1][x].kind == tile.Tile.PIECE:
            path_info[0] = find_depth(y - 1, x, 0, 7)
            path_info[1] = find_depth(y - 1, x, 0, 6)

        if game.board.board[y + 1][x].kind == tile.Tile.CLOSED or game.board.board[y + 1][x].kind == tile.Tile.START:
            path_info[6][0] = 1
            path_info[7][0] = 1
        elif game.board.board[y + 1][x].kind == tile.Tile.PIECE:
            path_info[6] = find_depth(y + 1, x, 0, 1)
            path_info[7] = find_depth(y + 1, x, 0, 0)

        if x % 2:
            if (game.board.board[y + 1][x + 1].kind == tile.Tile.CLOSED or
                    game.board.board[y + 1][x + 1].kind == tile.Tile.START):
                path_info[4][0] = 1
                path_info[5][0] = 1
            elif game.board.board[y + 1][x + 1].kind == tile.Tile.PIECE:
                path_info[4] = find_depth(y + 1, x + 1, 0, 11)
                path_info[5] = find_depth(y + 1, x + 1, 0, 10)

            if (game.board.board[y + 1][x - 1].kind == tile.Tile.CLOSED or
                    game.board.board[y + 1][x - 1].kind == tile.Tile.START):
                path_info[8][0] = 1
                path_info[9][0] = 1
            elif game.board.board[y + 1][x - 1].kind == tile.Tile.PIECE:
                path_info[8] = find_depth(y + 1, x - 1, 0, 3)
                path_info[9] = find_depth(y + 1, x - 1, 0, 2)

            if (game.board.board[y][x + 1].kind == tile.Tile.CLOSED or
                    game.board.board[y][x + 1].kind == tile.Tile.START):
                path_info[2][0] = 1
                path_info[3][0] = 1
            elif game.board.board[y][x + 1].kind == tile.Tile.PIECE:
                path_info[2] = find_depth(y, x + 1, 0, 9)
                path_info[3] = find_depth(y, x + 1, 0, 8)

            if (game.board.board[y][x - 1].kind == tile.Tile.CLOSED or
                    game.board.board[y][x - 1].kind == tile.Tile.START):
                path_info[10][0] = 1
                path_info[11][0] = 1
            elif game.board.board[y][x - 1].kind == tile.Tile.PIECE:
                path_info[10] = find_depth(y, x - 1, 0, 5)
                path_info[11] = find_depth(y, x - 1, 0, 4)

        else:
            if (game.board.board[y - 1][x + 1].kind == tile.Tile.CLOSED or
                    game.board.board[y - 1][x + 1].kind == tile.Tile.START):
                path_info[2][0] = 1
                path_info[3][0] = 1
            elif game.board.board[y - 1][x + 1].kind == tile.Tile.PIECE:
                path_info[2] = find_depth(y - 1, x + 1, 0, 9)
                path_info[3] = find_depth(y - 1, x + 1, 0, 8)

            if (game.board.board[y - 1][x - 1].kind == tile.Tile.CLOSED or
                    game.board.board[y - 1][x - 1].kind == tile.Tile.START):
                path_info[10][0] = 1
                path_info[11][0] = 1
            elif game.board.board[y - 1][x - 1].kind == tile.Tile.PIECE:
                path_info[10] = find_depth(y - 1, x - 1, 0, 5)
                path_info[11] = find_depth(y - 1, x - 1, 0, 4)

            if (game.board.board[y][x + 1].kind == tile.Tile.CLOSED or
                    game.board.board[y][x + 1].kind == tile.Tile.START):
                path_info[4][0] = 1
                path_info[5][0] = 1
            elif game.board.board[y][x + 1].kind == tile.Tile.PIECE:
                path_info[4] = find_depth(y, x + 1, 0, 11)
                path_info[5] = find_depth(y, x + 1, 0, 10)

            if (game.board.board[y][x - 1].kind == tile.Tile.CLOSED or
                    game.board.board[y][x - 1].kind == tile.Tile.START):
                path_info[8][0] = 1
                path_info[9][0] = 1
            elif game.board.board[y][x - 1].kind == tile.Tile.PIECE:
                path_info[8] = find_depth(y, x - 1, 0, 3)
                path_info[9] = find_depth(y, x - 1, 0, 2)

        path_info[entry_point] = [-1, -1, -1, -1]

        # print(f'Paths: {path_info} on {y} {x}')

        # state must be one long array of numbers
        # index legend: 0 / entry point
        # 1 - 48 / path info
        # 49 - 60 / curr tile connects
        # 61 - 72 / swap tile connects

        state = [entry_point] + [elem for sublist in path_info for elem in sublist][:48]

        for value in game.board.cur_tile.connects.values():
            state.append(value)

        for value in game.board.swap_tile.connects.values():
            state.append(value)

        # print(state)
        # return [entry_point, path_info, game.board.cur_tile, game.board.swap_tile]
        return state

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        self.epsilon = 600 - self.number_of_games
        final_move = [0, 0]
        modified_move = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 5)
            swap = random.randint(0, 1)
            modified_move[final_move[0]] = 1
            modified_move[6] = final_move[1]
            if swap == 0:
                modified_move[move] = 1
            else:
                modified_move[move+6] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move_prediction = prediction[0:6]
            swap_prediction = prediction[6]
            move = torch.argmax(move_prediction).item()
            swap = 1 if torch.argmax(swap_prediction).item() else 0
            final_move[0] = move
            final_move[1] = swap


            if swap == 0:
                modified_move[move] = 1
            else:
                modified_move[move+6] = 1

        return modified_move


def train():
    plot_scores = []
    plot_average_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    board = Board()
    game = Reader(board)
    done = True
    paused = False
    brojac = 0

    while done:
        if not paused:
            state_old = agent.get_state(game)  # get old state
            final_move = agent.get_action(state_old)  # new move
            reward, game_over, score = game.play_step(final_move, True)  # perform move
            state_new = agent.get_state(game)  # get new state after previous move
            agent.train_short_memory(state_old, final_move, reward, state_new, game_over)
            agent.remember(state_old, final_move, reward, state_new, game_over)

            if game_over:
                # paused = True
                game.reset()
                agent.number_of_games += 1
                agent.train_long_memory()

                if score > record:
                    record = score
                    agent.model.save()

                # print('Game:', agent.number_of_games, 'Score:', score, 'Record:', record)

                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.number_of_games
                plot_average_scores.append(mean_score)
                #plot(plot_scores, plot_average_scores)
                if (brojac % 100 == 0): print("" + brojac.__str__() + " " + mean_score.__str__() + " " + record.__str__())
                brojac = brojac + 1
        else:
            time.sleep(0.05)
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
        #         done = False
        #     elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
        #         paused = not paused


if __name__ == '__main__':
    train()

# state = get_state(game)
# action = get_move(state)   first will be random
# reward, game_over, score = game.play_step(action)
# new_state = get_state(game)
# remember?
