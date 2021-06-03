from random import randint
from typing import List

# from Scene.class_scene_Gl_2d_resize import BaseGl2dScaleScene, glutTimerFunc, glGenLists, GL_COMPILE, glNewList, \
#     glEndList, glDeleteLists, glCallList, Scene2d
from OpenGL.GLUT import glutTimerFunc
from Scene.magnet_scene_GL import MagnetsBaseScene, glCallList, Scene2d, glDeleteLists, glGenLists, glNewList, \
    GL_COMPILE, glEndList


class DataItem:
    x = 0
    y = 0
    value = 0

    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value


class FloodFill(MagnetsBaseScene):
    def get_color_item(self, value):
        if 1 == value:
            return self.get_color(255, 0, 0)
        if 2 == value:
            return self.get_color(0, 255, 0)
        if 3 == value:
            return self.get_color(0, 0, 255)
        if 4 == value:
            return self.get_color(255, 255, 0)

        return self.get_color(0, 0, 0)

    def rectangle_point(self, x1, y1, x2, y2):
        # gen_draw
        return [[x1, y1], [x1, y2], [x2, y2], [x2, y1]]

    timer_interval = 10
    diff_size_data = 100

    data: List[DataItem] = []

    size_xy = 5

    def timer_callback(self, el=0):
        # print(el)
        # if len(self.data) < self.diff_size_data:
        self.add_random_point()
        glutTimerFunc(self.timer_interval, self.timer_callback, el + 1)  # 0 - command

    def add_random_point(self):
        self.data.append(
            DataItem(
                randint(-10, 10),
                randint(-10, 10),
                randint(0, 4),
            )
        )
        self.gen_draw()

    def init(self):
        super().init()
        self.timer_callback()

    def gen_draw(self):
        # self.clear_lists()
        self.draw_obj()

    lists = []

    def redraw(self):
        for x in self.lists:
            glCallList(x)

        return super(Scene2d, self).redraw()

    # прегенерация объекта чтобы не рисовать каждый раз
    def draw_obj(self):
        length = len(self.data)
        cur = length // self.diff_size_data
        # print(length, len(self.lists), len(self.data[cur*self.diff_size_data:]))
        # if length != len(self.data[cur*self.diff_size_data:]) + cur * self.diff_size_data:
        #     print('error')
        if len(self.lists) <= cur:
            self.lists.append(0)

        glDeleteLists(self.lists[cur], 1)

        tmp = glGenLists(1)
        glNewList(tmp, GL_COMPILE)
        for p in self.data[cur*self.diff_size_data:]:
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


t = FloodFill(640, 480)
t.draw()
