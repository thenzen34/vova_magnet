from random import shuffle

from Scene.magnet_scene_GL import *

from floodfill import PointDataItem, FloodFill, timing
from lava_game import NOTHING, variants, WATER


class LavaGameScene(FloodFill):
    queue = []

    timer_interval = 1
    diff_size_data = 1000
    water_index = 70
    per_tick = 50
    shuffle_step = True

    def gl_key_pressed(self, *args):
        super().gl_key_pressed(*args)
        if args[0] == b" ":
            self.timer_callback()


    @timing
    def timer_callback(self, el=0):
        # while True:
        #     if self.add_random_point():
        #         break
        for i in range(self.per_tick):
            self.add_random_point()
        self.draw_obj()
        if len(self.queue) > 0:
            glutTimerFunc(self.timer_interval, self.timer_callback, el + 1)  # 0 - command

    def get_data(self, x, y):
        # if x < 0 or y < 0 or x >= self.width or y >= self.height:
        #     return NOTHING
        find = self.storage.has(PointDataItem((x, y, 0)), 0.1)
        if find >= 0:
            return self.storage.data[find].value
        else:
            return NOTHING

    def get_variants(self, x, y):
        result = self.get_data(x, y)
        return variants[result].copy()

    def set_data(self, x, y, value):
        self.storage.append(PointDataItem((x, y, value)))

    def is_clear(self, x, y):
        return self.get_data(x, y) == NOTHING

    def set_item(self, x, y, items):
        value = NOTHING
        if randint(0, 100 - 1) > self.water_index:
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
        # if x < 0 or y < 0 or x >= self.width or y >= self.height:
        #     return

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

    def add_random_point(self):
        if len(self.queue) > 0:
            x, y = self.queue.pop()

            items = list(self.has_conflict(x, y))

            if len(items) < 1:
                self.queue.clear()
                return True

            self.set_item(x, y, items)

            # print(x, y, items, len(self.queue))

            # if len(self.queue) > 20:
            #     self.queue.clear()
            #     return True

            all_steps = []
            all_steps.append((x - 1, y - 1))
            all_steps.append((x - 1, y))
            all_steps.append((x - 1, y + 1))
            all_steps.append((x, y + 1))
            all_steps.append((x + 1, y + 1))
            all_steps.append((x + 1, y))
            all_steps.append((x + 1, y - 1))
            all_steps.append((x, y - 1))

            if self.shuffle_step:
                shuffle(all_steps)

            for step in all_steps:
                self.add_to_queue(*step)

        return False

    def init(self):
        self.add_to_queue(0, 0)

        super(FloodFill, self).init()


t = LavaGameScene(640, 480)
t.draw()
