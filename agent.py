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

        # Need info for every each one of 12 paths - danger or not, if not, how much plates till out, where out
        path_info = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                     [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

        def find_depth(y1, x1, depth, direction):
            print(f'{y1} {x1} and {y} {x} on depth {depth} and looking at path {direction}')
            if y1 == y and x1 == x:
                print(f'{y1} {x1} and {y} {x} and it looped')
                return [-1, -1, -1, -1]
            if game.board.board[y1][x1].kind == tile.Tile.OPEN:
                print("current tile is open")
                return [0, depth, y1, x1]
            elif game.board.board[y1][x1].kind == tile.Tile.CLOSED or game.board.board[y1][x1].kind == tile.Tile.START:
                print("current tile is closed or start, aka danger")
                return [1, depth, y1, x1]
            else:
                print("current tile is a placed piece")
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

        print(f'Calling find depth for {y} and {x}')
        if (y, x) in closed:
            return [entry_point, path_info, game.board.cur_tile]

        if game.board.board[y - 1][x].kind == tile.Tile.CLOSED or game.board.board[y - 1][x].kind == tile.Tile.START:
            path_info[0][0] = 1
            path_info[1][0] = 1
        elif game.board.board[y-1][x].kind == tile.Tile.PIECE:
            path_info[0] = find_depth(y - 1, x, 0, 7)
            path_info[1] = find_depth(y - 1, x, 0, 6)

        if game.board.board[y + 1][x].kind == tile.Tile.CLOSED or game.board.board[y + 1][x].kind == tile.Tile.START:
            path_info[6][0] = 1
            path_info[7][0] = 1
        elif game.board.board[y+1][x].kind == tile.Tile.PIECE:
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



        # if (y - 1, x) in closed:
        #     danger[0] = 1
        # if (y + 1, x) in closed:
        #     danger[3] = 1
        # if (y, x + 1) in closed:
        #     if x % 2:
        #         danger[1] = 1
        #     else:
        #         danger[2] = 1
        # if (y, x - 1) in closed:
        #     if x % 2:
        #         danger[5] = 1
        #     else:
        #         danger[4] = 1
        # if x % 2:
        #     if (y + 1, x + 1) in closed:
        #         danger[2] = 1
        #     if (y + 1, x - 1) in closed:
        #         danger[4] = 1
        # else:
        #     if (y - 1, x + 1) in closed:
        #         danger[1] = 1
        #     if (y - 1, x - 1) in closed:
        #         danger[5] = 1


        # for i in range(6):
        #     if danger[i] == 0:
        #         pass
        #     else:
        #         path_info[i*2][0] = 1
        #         path_info[i*2+1][0] = 1

        path_info[entry_point] = [-1, -1, -1, -1]

        print(f'Paths: {path_info} on {y} {x}')

        return [entry_point, path_info, game.board.cur_tile, game.board.swap_tile]

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
        # self.epsilon = 80 - self.number_of_games
        # final_move = [0, 0]
        dangerous = True
        entry_point = state[0]
        path_info = state[1]
        cur_tile = state[2]
        swap_tile = state[3]
        # print(f'Cuttenr: {cur_tile}, Entry: {entry_point}, Paths: {path_info}')
        swap = 0
        max_score = 0
        best_move = 0
        clean = True
        for move in range(0, 6):
            new_entry = (entry_point - move * 2) % 12
            exit_point = (cur_tile.connects[new_entry] + move * 2) % 12
            if path_info[exit_point][0] == 0:
                if max_score <= path_info[exit_point][1]:
                    max_score = path_info[exit_point][1]
                    best_move = move
                    clean = False

        for move in range(0, 6):
            new_entry = (entry_point - move * 2) % 12
            exit_point = (swap_tile.connects[new_entry] + move * 2) % 12
            if path_info[exit_point][0] == 0:
                if max_score < path_info[exit_point][1]:
                    max_score = path_info[exit_point][1]
                    best_move = move
                    swap = 1
                    clean = False

        if clean:
            for move in range(0, 6):
                new_entry = (entry_point - move * 2) % 12
                exit_point = (cur_tile.connects[new_entry] + move * 2) % 12
                if max_score <= path_info[exit_point][1]:
                    max_score = path_info[exit_point][1]
                    best_move = move

            for move in range(0, 6):
                new_entry = (entry_point - move * 2) % 12
                exit_point = (swap_tile.connects[new_entry] + move * 2) % 12
                if max_score < path_info[exit_point][1]:
                    max_score = path_info[exit_point][1]
                    best_move = move
                    swap = 1

        # while dangerous:
        #     counter += 1
        #     move = random.randint(0, 5)
        #     new_entry = (entry_point - move * 2) % 12
        #     exit_point = (cur_tile.connects[new_entry] + move * 2) % 12
        #     # print(f'move: {move}, Entrynew: {new_entry}, exit: {exit_point}')
        #     if path_info[exit_point][0] == 0:
        #         dangerous = False
        #     if counter > 50:
        #         # swap tile
        #         swap = 1
        #         cur_tile = swap_tile
        #     if counter > 100:
        #         return [0, 1]

        final_move = [best_move, swap]
        print(final_move)
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
            state_new = agent.get_state(game)  # get new state after previous move
            # agent.train_short_memory(state_old, final_move, reward, state_new, game_over)
            # agent.remember(state_old, final_move, reward, state_new, game_over)

            if game_over:
                paused = True
                game.reset()
                agent.number_of_games += 1
                # agent.train_long_memory()

                if score > record:
                    record = score
                    # TODO agent.model.save()

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

# state = get_state(game)
# action = get_move(state)   first will be random
# reward, game_over, score = game.play_step(action)
# new_state = get_state(game)
# remember?
