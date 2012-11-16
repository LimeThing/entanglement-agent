import sys
import re
from threading import Thread

import tile
from tile import Board

class Main(object):
    def __init__(self, board, funsies):
        pygame.init()

        d = pygame.display.Info()
        self.desktop_size = (d.current_w, d.current_h)
        self.size = (600, 600)

        pygame.display.set_caption("Entanglement Client")

        self.done = False
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill((0xFF, ) * 3)

        self.funsies = funsies
        self.board = board
        self.clicked = 0
        self.ui = GameUI(self, None)

    def ui_push(self, cls):
        self.ui = cls(self, self.ui)

    def ui_pop(self):
        self.ui = self.ui.parent

    def ui_swap(self, cls):
        self.ui = cls(self, self.ui.parent)

    def stop(self):
        self.done = True

    def run(self):
        while not self.done:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                elif self.funsies:
                    if event.type == pygame.KEYDOWN:
                        self.ui.handle_key(event)
                    elif event.type == pygame.KEYUP:
                        self.ui.handle_key_up(event)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.clicked = True
                            self.ui.handle_click(event)
                        elif event.button in (4, 5):  # scrollin!
                            event.scroll_dir = event.button * 2 - 9
                            self.ui.handle_scroll(event)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.clicked = False
                            self.ui.handle_click_up(event)
                    elif event.type == pygame.MOUSEMOTION:
                        if event.buttons[0]:
                            self.ui.handle_drag(event)
                        else:
                            self.ui.handle_motion(event)

            self.screen.fill((0, ) * 3)
            self.ui.update()
            self.ui.reblit(self.screen)
            pygame.display.flip()
        pygame.quit()

class Reader(Thread):
    def __init__(self, board):
        super(Reader, self).__init__()
        self.board = board
        self.kill = False

    def stop(self):
        self.kill = True

    def run(self):
        keep_playing = True
        print self.board.swap_tile, "|", self.board.cur_tile
        while not self.kill and keep_playing:
            inp = raw_input(">")
            if inp == "quit":
                break
            matchobj = regex.match(inp)
            if matchobj:
                if matchobj.group(1) == "swap ":
                    self.board.swap()
                self.board.rotate(int(matchobj.group(2)))
                keep_playing = self.board.place()
                if keep_playing is not False:
                    print keep_playing
            else:
                print "Malformed input."


if __name__ == "__main__":
    regex = re.compile("(swap )?rotate (-?[0-5])")
    if "-s" in sys.argv[1:-1]:
        tile.random.seed(sys.argv[sys.argv[1:].index("-s") + 1])
    board = Board()
    funsies = False
    reader = None

    if "--nocmd" in sys.argv[1:]:
        funsies = True
    else:
        reader = Reader(board)
        reader.start()

    if "--nogui" not in sys.argv[1:]:
        import pygame
        from ui.game import GameUI
        game = Main(board, funsies)
        game.run()
        if reader is not None:
            reader.stop()
