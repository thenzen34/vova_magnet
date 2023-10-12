import random

from Scene.magnet_scene_GL import *

from magnet_data_class import MagnetsData


class UntagleScene(MagnetsData, MagnetsBaseScene):

    # debug = True
    def gl_key_pressed(self, *args):
        super().gl_key_pressed(*args)

        cmd = args[0]
        if cmd == b"r":
            self.reset_scene()

    def reset_scene(self):
        self.reset_system()
        cnt = 5
        max_xy = 200
        for x in range(cnt):
            self.new_ball(random.randint(-max_xy, max_xy), random.randint(-max_xy, max_xy), self.length, self.r)

        from stick_class import Stick
        for i in range(cnt-1):#0..cnt-2
            for j in range(i, cnt):#i..cnt-1
                if random.random() > 0.5:
                    self.sticks.append(Stick(i, j))
        self.gen_draw()

    """
    для двойного клика правки в on_mouse_click
    """

    def init(self):
        super().init()
        self.reset_scene()

    def get_real_xy(self, x, y):
        n_x, n_y = self.get_scene_xy(self.ddx, self.ddy)
        n_x -= self.width / 2
        n_y -= self.height / 2

        cur_x, cur_y = (x - self.width / 2) / self.nSca - n_x, (y - self.height / 2) / self.nSca - n_y
        return cur_x, cur_y

    def on_mouse_left_up(self, x, y):
        self.last_ball = -1
        self.gen_draw()
        super().on_mouse_left_up(x, y)

    def on_mouse_left_down(self, x, y):
        cur_x, cur_y = self.get_real_xy(x, y)

        # select start ball
        # проверяем клик по шарам
        i = 0
        while i < len(self.not_virtual):
            ix = self.not_virtual[i]
            if self.balls[ix].check_click(cur_x, cur_y):
                if self.last_ball < 0:
                    self.last_ball = ix
                    self.gen_draw()
                # if tool.on_mouse_left_down(cur_x, cur_y):
                #     return True
                break
            i += 1

        super().on_mouse_left_down(x, y)

    cur_x = 0.
    cur_y = 0.

    def gl_mouse_motion(self, x, y):
        self.cur_x = x
        self.cur_y = y

        cur_x, cur_y = self.get_real_xy(x, y)
        if self.last_ball >= 0:
            self.balls[self.last_ball].x = cur_x
            self.balls[self.last_ball].y = cur_y

            self.gen_draw()

        return super().gl_mouse_motion(x, y)

    def redraw(self):
        super().redraw()

        return self

    def draw_obj(self):
        # type: () -> UntagleScene
        self.show_move = True

        i = 0
        while i < len(self.balls):
            # for ball in self.balls:
            ball = self.balls[i]
            if ball.enable:
                g = 0
                if self.last_ball == i:
                    g = 255
                if ball.virtual:
                    self.c_set_color(100, 0, g)
                else:
                    self.c_set_color(255, 0, g)
                self.i_move_to(*ball.get_xy()).put_ball()  # .i_draw_text(str(ball.s_id))

                self.i_push_step().c_push_color().d_push_digital_size()
                self.c_set_color(100, 200, 100).d_set_digital_size(1).d_draw_tex(str(ball.s_id), True)
                self.i_pop_step().c_pop_color().d_pop_digital_size()
            i += 1

        for stick in self.sticks:
            ball_start = self.balls[stick.start_ball_id]
            ball_end = self.balls[stick.end_ball_id]
            self.c_set_color(0, 100, 200).i_move_to(*ball_start.get_xy()).i_line_to(*ball_end.get_xy())

        self.i_push_step().c_push_color().d_push_digital_size()
        self.c_set_color(200, 100, 200).i_move_to(0, 480).d_draw_tex('b:{0} s:{1} p:{2} r:{3}'.format(
            len(self.balls),
            len(self.sticks),
            sum([len(x.parents_id) for x in self.balls]),
            len(self.all_balls_r),
        ), True)

        # self.c_set_color(200, 100, 200).i_move_to(0, -480).d_draw_tex('0123456789 ABCDEFGHIJKLMNOPQRSTUVWXYZ АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', True)
        self.i_pop_step().c_pop_color().d_pop_digital_size()

        return self


t = UntagleScene(640, 480)
t.draw()

# TODO undo
#  переделать ссылки по id -> object_pointer ?
#  рефакторинг сцены разбить на независимые участки - текст, геометрия, цвет, ..
#  move object tool, info
