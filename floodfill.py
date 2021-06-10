import math
from random import randint
from typing import List, TypeVar, Generic  # overload

# from Scene.class_scene_Gl_2d_resize import BaseGl2dScaleScene, glutTimerFunc, glGenLists, GL_COMPILE, glNewList, \
#     glEndList, glDeleteLists, glCallList, Scene2d
from OpenGL.GLUT import glutTimerFunc
from Scene.magnet_scene_GL import MagnetsBaseScene, glCallList, Scene2d, glDeleteLists, glGenLists, glNewList, \
    GL_COMPILE, glEndList

from lava_game import SAND, WATER, GROUND, LAVA
from magnet_data_class import find_right_b, find_left_b

MAX_SIZE_XY = 1


def timing(f):
    from functools import wraps
    from time import time

    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        if te - ts > 1:
            print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te - ts))
        return result

    return wrap


class DataItem:
    @timing
    def __init__(self, p):
        pass

    @timing
    def get_ix_info(self):
        return -1

    @timing
    def check(self, item: 'DataItem'):
        return False

    @timing
    def __str__(self):
        return "-"


class PointDataItem(DataItem):
    x = 0
    y = 0
    value = 0

    @timing
    def __init__(self, p):
        super().__init__(p)
        self.x, self.y, self.value = p

    @timing
    def get_ix_info(self):
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))

    @timing
    def check(self, item: 'PointDataItem'):
        length = math.sqrt(pow(item.x - self.x, 2) + pow(item.y - self.y, 2))
        # print('l', length, item.x, self.x)
        # return self.x == item.x and self.y == item.y
        return length < 1

    @timing
    def __str__(self):
        return "{0}:{1}".format(self.x, self.y)


T = TypeVar('T')


class DataStorage(Generic[T]):
    data: List[T] = []
    ix = []

    @timing
    def append(self, item: DataItem):
        s_id = len(self.data)

        r = item.get_ix_info()
        ix = find_left_b(self.ix, r)
        if ix + 1 > len(self.ix):
            self.ix.append((s_id, r))
        else:
            self.ix.insert(ix, (s_id, r))

        self.data.append(item)

    @timing
    def has(self, item: DataItem, cur_r):
        r = item.get_ix_info()

        start_ix = find_left_b(self.ix, r - cur_r)
        end_ix = find_right_b(self.ix, r + cur_r)

        # print('start_ix..=', start_ix, end_ix, self.ix)
        # for i in self.data:
        #     print('data..', i)

        if len(self.ix):
            for i in range(start_ix, end_ix + 1):
                # print('s', i, len(self.ix))
                if len(self.ix) <= i:
                    # print('try..', item, i)
                    # print('start_ix..=', start_ix, end_ix, self.ix)
                    # for it in self.data:
                    #     print('data..', it)
                    pass
                else:
                    ix = self.ix[i][0]

                    if item.check(self.data[ix]):
                        # print('findzz ')
                        return ix

        return -1

    # @overload
    # def __add__(self, x: 'A') -> 'A': ...
    #     pass
    # https://stackoverflow.com/questions/2627002/whats-the-pythonic-way-to-use-getters-and-setters
    # https://habr.com/ru/post/437018/


# def default():
#     obj: DataStorage = DataStorage[PointDataItem]()
#     # obj.append(PointDataItem((1, 1, 1)))
#     obj.append(PointDataItem((0, 0, 1)))
#     # obj.append(PointDataItem((-1, -1, 1)))
#     # for _ in range(10):
#     #     obj.append(PointDataItem(
#     #         (
#     #             randint(-MAX_SIZE_XY, MAX_SIZE_XY),
#     #             randint(-MAX_SIZE_XY, MAX_SIZE_XY),
#     #             randint(-MAX_SIZE_XY, MAX_SIZE_XY),
#     #         )
#     #     )
#     #     )
#     print('h', obj.has(PointDataItem((1, 1, 1)), 0.1))
#     print('h', obj.has(PointDataItem((1, 0, 1)), 0.1))
#     print('h', obj.has(PointDataItem((0, 1, 1)), 0.1))
#     print('h', obj.has(PointDataItem((0, 0, 1)), 0.1))
#
#
# def test1():
#     obj: DataStorage = DataStorage[PointDataItem]()
#     obj.append(PointDataItem((0, 0, 1)))
#
# default()
# exit()


class FloodFill(MagnetsBaseScene):
    @timing
    def get_color_item(self, value):
        if LAVA == value:
            return self.get_color(255, 0, 0)
        if GROUND == value:
            return self.get_color(0, 255, 0)
        if WATER == value:
            return self.get_color(0, 0, 255)
        if SAND == value:
            return self.get_color(255, 255, 0)

        return self.get_color(255, 255, 255)

    @timing
    def rectangle_point(self, x1, y1, x2, y2):
        # gen_draw
        return [[x1, y1], [x1, y2], [x2, y2], [x2, y1]]

    timer_interval = 1000
    diff_size_data = 100

    storage: DataStorage[PointDataItem] = DataStorage()

    size_xy = 50

    @timing
    def timer_callback(self, el=0):
        # print(el)
        # print(math.pow(MAX_SIZE_XY * 2 + 1, 2))
        if len(self.storage.data) < math.pow(MAX_SIZE_XY * 2 + 1, 2):
            while True:
                if self.add_random_point():
                    break
            glutTimerFunc(self.timer_interval, self.timer_callback, el + 1)  # 0 - command
        else:
            for i in self.storage.data:
                print('data..', i)

    @timing
    def add_random_point(self):
        return self.add_point(
            randint(-MAX_SIZE_XY, MAX_SIZE_XY),
            randint(-MAX_SIZE_XY, MAX_SIZE_XY),
            randint(0, 4),
        )

    @timing
    def add_point(self, x, y, val):
        item = PointDataItem(
            (
                x, y, val
            )
        )
        find = self.storage.has(item, 0.01)
        # print('find ', find)
        if find < 0:
            self.storage.append(
                item
            )
            # print('len= ', len(self.storage.data))
            self.gen_draw()
            return True
        return False

    @timing
    def init(self):
        super().init()
        self.timer_callback()

    @timing
    def gen_draw(self):
        # self.clear_lists()
        self.draw_obj()

    lists = []

    @timing
    def redraw(self):
        for x in self.lists:
            glCallList(x)

        return super(Scene2d, self).redraw()

    @timing
    # прегенерация объекта чтобы не рисовать каждый раз
    def draw_obj(self):
        length = len(self.storage.data)
        cur = length // self.diff_size_data
        # print(length, len(self.lists), len(self.data[cur*self.diff_size_data:]))
        # if length != len(self.data[cur*self.diff_size_data:]) + cur * self.diff_size_data:
        #     print('error')
        if len(self.lists) <= cur:
            self.lists.append(0)

        glDeleteLists(self.lists[cur], 1)

        tmp = glGenLists(1)
        glNewList(tmp, GL_COMPILE)
        for p in self.storage.data[cur * self.diff_size_data:]:
            points = self.rectangle_point(
                (p.x) * self.size_xy + 1,
                (p.y) * self.size_xy + 1,
                (p.x + 1) * self.size_xy - 1,
                (p.y + 1) * self.size_xy - 1
            )
            self.fill_points(self.get_color_item(p.value), points)
            # self.setpixels([(p.x, p.y)], self.get_color_item(p.value))
        glEndList()
        self.lists[cur] = tmp


if __name__ == '__main__':
    t = FloodFill(640, 480)
    t.draw()
