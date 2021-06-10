from Scene.magnet_scene_GL import *
from time import sleep


class LavaGameScene(MagnetsBaseScene):
    def init(self):
        super().init()

    def draw_obj(self):
        # type: () -> LavaGameScene
        self.show_move = True

        self.c_set_color(0, 255, 0).i_circle(20)

        return self


# t = LavaGameScene(640, 480)
# t.draw()

def lava_print(string):
    print('\x1b[41m \x1b[0m', end=' ')


def green_print(string):
    print('\x1b[42m \x1b[0m', end=' ')


def water_print(string):
    print('\x1b[44m \x1b[0m', end=' ')


def yellow_print(string):
    print('\x1b[43m \x1b[0m', end=' ')


# The screen clear function
def screen_clear():
    # for mac and linux(here, os.name is 'posix')
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')
    # print out some text


NOTHING = 0
LAVA = 1
GROUND = 2
SAND = 3
WATER = 4

conflict = {
    NOTHING: [],
    LAVA: [GROUND, SAND],
    GROUND: [LAVA],
    SAND: [LAVA],
    WATER: []
}

variants = {
    NOTHING: {LAVA, GROUND, SAND, WATER},
    LAVA: {LAVA, WATER},
    GROUND: {GROUND, SAND, WATER},
    SAND: {GROUND, SAND, WATER},
    WATER: {LAVA, GROUND, SAND, WATER}
}
size = 15


class LavaGame:
    def __init__(self, width=4 * size, height=3 * size):
        self.width = width
        self.height = height
        self.data = []
        self.queue = []
        self.reset()

    def reset(self):
        self.data = [[NOTHING for _ in range(self.width)] for _ in range(self.height)]

    def get_data(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return NOTHING
        return self.data[y][x]

    def get_variants(self, x, y):
        result = self.get_data(x, y)
        return variants[result].copy()

    def set_data(self, x, y, value):
        self.data[y][x] = value

    def is_clear(self, x, y):
        return self.get_data(x, y) == NOTHING

    def set_item(self, x, y, items):
        value = NOTHING
        if randint(0, 100-1) > 100:
            value = WATER
        else:
            length = len(items)
            is_find = False
            while not is_find:
                if length:
                    ix = randint(0, length - 1)
                    value = items[ix]
                    # print(ix, value)

                is_find = True
                if WATER == value and length > 1:
                    if randint(0, 100 - 1) > 30:
                        is_find = False
        self.set_data(x, y, value)
        return value

    def add_to_queue(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return

        if not self.is_clear(x, y):
            return

        if (x, y) in self.queue:
            return
        self.queue.insert(0, (x, y))

    def has_conflict(self, x, y):
        result = variants[NOTHING].copy()

        result &= self.get_variants(x, y)
        # print(result)
        result &= self.get_variants(x - 1, y - 1)
        # print(result)
        result &= self.get_variants(x - 1, y)
        # print(result)
        result &= self.get_variants(x - 1, y + 1)
        # print(result)
        result &= self.get_variants(x, y + 1)
        # print(result)
        result &= self.get_variants(x + 1, y + 1)
        # print(result)
        result &= self.get_variants(x + 1, y)
        # print(result)
        result &= self.get_variants(x + 1, y - 1)
        # print(result)
        result &= self.get_variants(x, y - 1)
        # print(result)

        return result

    def atack(self):
        while len(self.queue) > 0:
            x, y = self.queue.pop()

            items = list(self.has_conflict(x, y))

            if len(items) < 1:
                self.queue.clear()
                return

            self.set_item(x, y, items)

            self.add_to_queue(x - 1, y - 1)
            self.add_to_queue(x - 1, y)
            self.add_to_queue(x - 1, y + 1)
            self.add_to_queue(x, y + 1)
            self.add_to_queue(x + 1, y + 1)
            self.add_to_queue(x + 1, y)
            self.add_to_queue(x + 1, y - 1)
            self.add_to_queue(x, y - 1)

            # sleep(0.05)
            # self.dump(items)

    def color_print(self, value):
        if value == LAVA:
            print('\x1b[41m  \x1b[0m', end='')
        elif value == GROUND:
            print('\x1b[42m  \x1b[0m', end='')
        elif value == SAND:
            print('\x1b[43m  \x1b[0m', end='')
        elif value == WATER:
            print('\x1b[44m  \x1b[0m', end='')
        else:
            print('\x1b[40m  \x1b[0m', end='')

    def set_random(self, val):
        x = randint(0, self.width - 1)
        y = randint(0, self.height - 1)

        self.set_item(x, y, [val])

    def draw(self):
        # for _ in range(size):
        #     self.set_random(LAVA)
        # for _ in range(size):
        #     self.set_random(WATER)
        x = randint(0, self.width - 1)
        y = randint(0, self.height - 1)

        self.add_to_queue(x, y)

        self.atack()

        self.dump()

    def dump(self, value=None):
        if value is None:
            value = {}
        screen_clear()
        print(value)
        for line in self.data:
            for char in line:
                self.color_print(char)
            print()


if __name__ == '__main__':
    obj = LavaGame()
    obj.draw()
