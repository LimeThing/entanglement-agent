import random

class Tile(object):
    ALL_DIRS = range(12)
    UP_L, UP_R, RU_L, RU_R, RD_L, RD_R, DO_L, DO_R, LD_L, LD_R, LU_L, LU_R = ALL_DIRS
    INLINE = {  frozenset([UP_L, UP_R]),
                frozenset([RU_L, RU_R]),
                frozenset([RD_L, RD_R]),
                frozenset([DO_L, DO_R]),
                frozenset([LD_L, LD_R]),
                frozenset([LU_L, LU_R])}
    OPPOSITE = {UP_L: DO_R, UP_R: DO_L, RU_L: LD_R, RU_R: LD_L, RD_L: LU_R, RD_R: LU_L,
                DO_L: UP_R, DO_R: UP_L, LD_L: RU_R, LD_R: RU_L, LU_L: RD_R, LU_R: RD_L}
    OPEN, PIECE, CLOSED, START = range(4)

    def __init__(self, kind=PIECE):
        self.lit = set()
        self.connects = {}
        self.kind = kind
        if kind == Tile.PIECE:
            # for x, y in ((Tile.UP_L, Tile.UP_R), (Tile.RU_L, Tile.RU_R), (Tile.RD_L, Tile.RD_R),
            #         (Tile.DO_L, Tile.DO_R), (Tile.LD_L, Tile.LD_R), (Tile.LU_L, Tile.LU_R)):
            #     self.connects[x] = y
            #     self.connects[y] = x
            ###################################################################
            # for x, y in ((Tile.UP_R, Tile.RU_L), (Tile.RU_R, Tile.RD_L), (Tile.RD_R, Tile.DO_L),
            #         (Tile.DO_R, Tile.LD_L), (Tile.LD_R, Tile.LU_L), (Tile.LU_R, Tile.UP_L)):
            #     self.connects[x] = y
            #     self.connects[y] = x
            ###################################################################
            dirs_left = set(Tile.ALL_DIRS)
            for dr in Tile.ALL_DIRS:
                if dr not in dirs_left:
                    continue
                dirs_left.discard(dr)
                choice = random.sample(dirs_left, 1)[0]
                dirs_left.discard(choice)
                self.connects[dr] = choice
                self.connects[choice] = dr

    def light(self, dr):
        con = self.connects[dr]
        self.lit.add(dr)
        self.lit.add(con)
        return con

    def rotate(self, amt):
        """ This is nontrivial, do it infrequently. """
        amt = (amt % 6) * 2
        new_connects = {}
        num_sides = len(Tile.ALL_DIRS)
        for k, v in self.connects.iteritems():
            new_connects[(k + amt) % num_sides] = (v + amt) % num_sides
        self.connects = new_connects

    @staticmethod
    def dist((x1, y1), (x2, y2)):
        """ No guarantees this actually does what you want: had to do some voodoo magic. """
        y1 += (x1 - 1) // 2
        y2 += (x2 - 1) // 2
        dx = x1 - x2
        dy = y1 - y2
        dxy = dx - dy
        return max(map(abs, (dx, dy, dxy)))

    def __str__(self):
        seen = set()
        toR = ""
        for k, v in self.connects.iteritems():
            if k in seen:
                continue
            seen.add(v)
            toR = ''.join((toR, str(k), "-", str(v), ","))
        return toR[:-1]


class Board(object):
    def __init__(self):
        def lookup(dist):
            if dist == 0:
                return Tile.START
            elif dist <= 3:
                return Tile.OPEN
            else:
                return Tile.CLOSED
        self.board = [[Tile(lookup(Tile.dist((4, 4), (x, y))))
                        for x in xrange(9)]
                        for y in xrange(9)]
        self.entry = Tile.DO_R
        self.x = 4
        self.y = 3
        self.cur_tile = Tile(Tile.PIECE)
        self.swap_tile = Tile(Tile.PIECE)
        self.score = 0
        self.dirty = 0

    def _set_cur_tile(self, val):
        self.board[self.y][self.x] = val

    cur_tile = property(lambda self: self.board[self.y][self.x], _set_cur_tile)

    def swap(self):
        self.swap_tile, self.cur_tile = self.cur_tile, self.swap_tile
        self.dirty = 1

    def place(self):
        more_score = 0
        while self.cur_tile.kind == Tile.PIECE:
            more_score += 1
            self.score += more_score
            next_dir = self.cur_tile.light(self.entry)
            if next_dir in (Tile.UP_L, Tile.UP_R):
                self.y -= 1
            elif next_dir in (Tile.DO_L, Tile.DO_R):
                self.y += 1
            elif next_dir in (Tile.RU_L, Tile.RU_R):
                self.x += 1
                if self.x % 2:
                    self.y -= 1
            elif next_dir in (Tile.RD_L, Tile.RD_R):
                if self.x % 2:
                    self.y += 1
                self.x += 1
            elif next_dir in (Tile.LU_L, Tile.LU_R):
                self.x -= 1
                if self.x % 2:
                    self.y -= 1
            elif next_dir in (Tile.LD_L, Tile.LD_R):
                if self.x % 2:
                    self.y += 1
                self.x -= 1

            self.entry = Tile.OPPOSITE[next_dir]
        if self.cur_tile.kind in (Tile.CLOSED, Tile.START):    # game over!~
            print "You lose. Final score:", self.score
            return False
        elif self.cur_tile.kind == Tile.OPEN:
            self.cur_tile = Tile(Tile.PIECE)
        self.dirty = 1
        return self.cur_tile

    def rotate(self, amt):
        self.cur_tile.rotate(int(amt))
        self.dirty = 1

    def rotate_right(self):
        self.rotate(1)

    def rotate_left(self):
        self.rotate(-1)
