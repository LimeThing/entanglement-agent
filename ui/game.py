import pygame

from ui import UI
from tile import Tile

slen = 40
h = 0.86602540378 * slen
BUF = pygame.Surface((slen * 2, h * 2), pygame.SRCALPHA)

class GameUI(UI):
    DIR_MAPPINGS = {Tile.UP_L: (slen * 3 / 4, 0), Tile.UP_R: (slen * 5 / 4, 0),
                    Tile.RU_L: (slen * 5 / 3, h / 3), Tile.RU_R: (slen * 11 / 6, h * 2 / 3),
                    Tile.RD_L: (slen * 11 / 6, h * 4 / 3), Tile.RD_R: (slen * 5 / 3, h * 5 / 3),
                    Tile.DO_L: (slen * 5 / 4, h * 2), Tile.DO_R: (slen * 3 / 4, h * 2),
                    Tile.LD_L: (slen / 3, h * 5 / 3), Tile.LD_R: (slen / 6, h * 4 / 3),
                    Tile.LU_L: (slen / 6, h * 2 / 3), Tile.LU_R: (slen / 3, h / 3)}
    def __init__(self, main, parent):
        super(GameUI, self).__init__(main, parent)
        self.font = pygame.font.Font(None, 60)

        self.surface = pygame.Surface(main.size)
        self.draw_board()

    board = property(lambda self: self.main.board)

    def reblit(self, surf):
        if self.board.dirty:
            self.draw_board()
        surf.blit(self.surface, (0, 0))

    def draw_tile(self, tile, x, y):
        """ Carve the buffer, to allow same-side connections to be drawn with circles """
        LINE_THICKNESS = 3
        if tile.kind == Tile.PIECE:
            BUF.fill((0xEE, 0xDD, 0xAA))
            for k, v in tile.connects.items():
                comp = frozenset([k, v])
                color = (0x66, ) * 3
                if k in tile.lit:
                    color = (0x00, 0xEE, 0x44)
                if(comp in Tile.INLINE):
                    o, t = GameUI.DIR_MAPPINGS[k], GameUI.DIR_MAPPINGS[v]
                    center = (int((o[0] + t[0]) / 2), int((o[1] + t[1]) / 2))
                    pygame.draw.circle(BUF, color, center, slen // 4, LINE_THICKNESS)

                else:
                    pygame.draw.line(BUF, color, GameUI.DIR_MAPPINGS[k], GameUI.DIR_MAPPINGS[v], LINE_THICKNESS)
            pygame.draw.polygon(BUF, (0, ) * 4,
                [(slen * 3 / 2, 0), (slen * 2, h), (slen * 3 / 2, h * 2), (slen * 2, h * 2), (slen * 2, 0)])
            pygame.draw.polygon(BUF, (0, ) * 4,
                [(slen / 2, h * 2), (0, h), (slen / 2, 0), (0, 0), (0, h * 2)])
        elif tile.kind == Tile.OPEN:
            BUF.fill((0, ) * 4)
            pygame.draw.polygon(BUF, (0x44, ) * 3,
                [(slen / 2, 0), (slen * 3 / 2, 0),
                 (slen * 2, h), (slen * 3 / 2, h * 2),
                 (slen / 2, h * 2), (0, h)])
        elif tile.kind == Tile.START:
            BUF.fill((0, ) * 4)
            pygame.draw.line(BUF, (0x00, 0xEE, 0x44), (GameUI.DIR_MAPPINGS[Tile.UP_L]), (slen, h), LINE_THICKNESS)
        else:
            return
        self.surface.blit(BUF, (x, y))

    def handle_key(self, event):
        if event.key == pygame.K_LEFT:
            self.board.rotate_left()
        if event.key == pygame.K_RIGHT:
            self.board.rotate_right()
        if event.key == pygame.K_a:
            self.board.reset()
            self.draw_board()
        if event.key == pygame.K_SPACE:
            self.board.place()
        if event.key == pygame.K_TAB:
            self.board.swap()
        if event.key == pygame.K_s:
            self.board.random()
            self.draw_board()
        if event.key == pygame.K_d:
            connections = {}
            k, l = 1, 1
            for i in self.board.board:
                l = 1
                for j in i:
                    connections[k][l] = j.connects.items()
                    l += 1
                k += 1
            # print(connections)
        if event.key == pygame.K_p:
            pygame.event.post(self.pause_event)

    def draw_board(self):
        self.surface.fill((0, ) * 3)
        self.surface.blit(self.font.render(str(self.board.score), True, (0xFF, ) * 3), (0, 0))
        for y, row in enumerate(self.board.board):
            for x, elem in enumerate(row):
                self.draw_tile(elem, x * (3 * slen / 2 + 1), (y + (x % 2) / 2.0) * (h * 2 + 1))
        self.draw_tile(self.board.swap_tile, 0, self.main.size[1] - h * 2)
