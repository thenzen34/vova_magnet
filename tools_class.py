from Scene.magnet_scene_GL import MagnetsBaseScene
from magnet_data_class import MagnetsData


# типа контроллеры данных

class ToolsBase:
    def __init__(self, data=None, scene=None):
        """

        :type data: MagnetsData
        :type scene: MagnetsBaseScene
        """
        self.scene = scene
        self.data = data

        self.init()

    def init(self):
        pass

    def draw(self, cur_x, cur_y):
        """

        :param cur_x: float
        :param cur_y: float
        :return MagnetsBaseScene
        """
        return self.scene

    def click(self, cur_x, cur_y):
        """

        :param cur_x: float
        :param cur_y: float
        :return bool
        """
        return False

    def on_mouse_wheel_up(self, cur_x, cur_y):
        """

        :param cur_x: float
        :param cur_y: float
        :return bool
        """
        return False

    def on_mouse_wheel_down(self, cur_x, cur_y):
        """

        :param cur_x: float
        :param cur_y: float
        :return bool
        """
        return False

    def get_name(self):
        """

        :return str
        """
        return 'Unknown'

    def finish(self):
        self.data.last_ball = -1


class NoneTool(ToolsBase):
    def get_name(self):
        return 'None'

    def click(self, cur_x, cur_y):
        print('None click')
        return False

    def draw(self, cur_x, cur_y):
        # type: (float, float) -> ()
        """

        :param cur_y: float
        :param cur_x: float
        """
        r = 2
        return self.scene.i_push_step().i_move_to(cur_x - r, cur_y - r).i_circle(r).i_pop_step()


class BallTool(ToolsBase):
    def get_name(self):
        return 'Ball'

    def click(self, cur_x, cur_y):
        if self.data.last_ball >= 0:
            # check_click in virtual
            i = 0
            while i < len(self.data.virtual):
                ix = self.data.virtual[i]
                if self.data.balls[ix].check_click(cur_x, cur_y):
                    self.data.set_ball_not_virtual(ix)

                    self.data.last_ball = -1
                    return True
                i += 1
            # смотрим был ли клик по шарам
            i = 0
            while i < len(self.data.not_virtual):
                ix = self.data.not_virtual[i]
                if ix == self.data.last_ball:
                    self.data.last_ball = -1
                    self.data.clear_virtual_ball()
                    return True
                i += 1
        else:
            # выбираем родителя
            i = 0
            while i < len(self.data.not_virtual):
                ix = self.data.not_virtual[i]
                if self.data.balls[ix].check_click(cur_x, cur_y):
                    self.data.last_ball = ix

                    self.data.virtual += self.data.get_virtual_balls(ix, self.get_move_xy_function)
                    return True
                i += 1
        return False

    def get_move_xy_function(self, angle, length):
        c_x, c_y = self.scene.t_push_alfa().move_angle(angle).get_move_xy(length)
        self.scene.t_pop_alfa()
        return c_x, c_y

    def draw(self, cur_x, cur_y):
        # type: (float, float) -> ()
        """

        :param cur_y: float
        :param cur_x: float
        """
        self.scene.t_push_alfa().i_push_step().i_move_to(cur_x, cur_y).c_set_color(100, 100, 255)

        self.scene.put_ball()
        return self.scene.i_pop_step().t_pop_alfa()

    def finish(self):
        self.data.clear_virtual_ball()
        super().finish()


class StickTool(ToolsBase):
    REMOVE = True

    def get_name(self):
        return 'Stick'

    def click(self, cur_x, cur_y):
        all_stick_ball_ids = [sorted([x.start_ball_id, x.end_ball_id]) for x in self.data.sticks]
        # check_click in not virtual
        i = 0
        while i < len(self.data.not_virtual):
            ix = self.data.not_virtual[i]
            if self.data.balls[ix].check_click(cur_x, cur_y):
                if self.data.last_ball < 0:
                    self.data.last_ball = ix
                else:
                    if self.data.last_ball != ix and self.data.balls[self.data.last_ball].parents_id.count(ix) > 0:
                        result = sorted([self.data.last_ball, ix])
                        if all_stick_ball_ids.count(result) == 0:
                            self.data.new_stick(ix)
                        else:
                            if self.REMOVE:
                                ix_stick = all_stick_ball_ids.index(result)
                                self.data.remove_stick(ix_stick)
                    self.data.last_ball = -1
                return True
            i += 1
        return False


class DelBallTool(ToolsBase):
    def click(self, cur_x, cur_y):
        # удалить стики, связи у родителей, фикс очереди
        i = 0
        while i < len(self.data.not_virtual):
            ix = self.data.not_virtual[i]
            ball = self.data.balls[ix]
            if ball.check_click(cur_x, cur_y):
                self.data.remove_ball(ix)
                self.data.last_ball = -1
                return True
            i += 1
        return False

    def get_name(self):
        return 'Del ball'


class Ball3Tool(ToolsBase):
    angle = 0.
    dalfa = 0.
    cnt = 3

    def init(self):
        super().init()
        self.dalfa = 360 // self.cnt

    def get_name(self):
        return '{0} Ball'.format(self.cnt)

    def on_mouse_wheel_up(self, cur_x, cur_y):
        """

        :param cur_x: float
        :param cur_y: float
        :return bool
        """
        self.angle -= 30
        return True

    def on_mouse_wheel_down(self, cur_x, cur_y):
        """

        :param cur_x: float
        :param cur_y: float
        :return bool
        """
        self.angle += 30
        return True

    def click(self, cur_x, cur_y):
        # проверяем клик по шарам
        i = 0
        while i < len(self.data.not_virtual):
            ix = self.data.not_virtual[i]
            if self.data.balls[ix].check_click(cur_x, cur_y):
                # прикрепляем
                ball = self.data.balls[ix]

                # добавляем шары через BallTool
                tool_ball = BallTool(self.data, self.scene)
                tool_ball.click(cur_x, cur_y)

                self.scene.t_push_alfa()
                c_x, c_y = cur_x, cur_y
                for x in range(self.cnt - 1):
                    angle = self.angle + self.dalfa * x
                    d_x, d_y = tool_ball.get_move_xy_function(angle, ball.length)
                    c_x += d_x
                    c_y += d_y
                    tool_ball.click(c_x, c_y)
                    if x < self.cnt - 2:
                        tool_ball.click(c_x, c_y)

                self.scene.t_pop_alfa()
                self.data.last_ball = -1

                # добавляем стики через StickTool
                tool_stick = StickTool(self.data, self.scene)
                tool_stick.REMOVE = False
                tool_stick.click(cur_x, cur_y)

                self.scene.t_push_alfa()
                c_x, c_y = cur_x, cur_y
                for x in range(self.cnt):
                    angle = self.angle + self.dalfa * x
                    d_x, d_y = tool_ball.get_move_xy_function(angle, ball.length)
                    c_x += d_x
                    c_y += d_y
                    tool_stick.click(c_x, c_y)
                    if x < self.cnt - 1:
                        tool_stick.click(c_x, c_y)

                self.scene.t_pop_alfa()
                self.data.last_ball = -1
                return True
            i += 1

        # self.angle += 30
        return False

    def draw(self, cur_x, cur_y):
        # type: (float, float) -> ()
        """

        :param cur_y: float
        :param cur_x: float
        """
        self.scene.t_push_alfa().i_push_step().i_move_to(cur_x, cur_y).move_angle(self.angle).c_set_color(100, 100, 255)

        for x in range(self.cnt):
            self.scene.put_stick_and_ball().move_dalfa(self.dalfa)
        return self.scene.i_pop_step().t_pop_alfa()


class Ball4Tool(Ball3Tool):
    cnt = 4


'''
class Ball5Tool(Ball3Tool):
    cnt = 5
'''


class Ball6Tool(Ball3Tool):
    cnt = 6

class LineTool(ToolsBase):
    def get_name(self):
        return 'Line'

    def click(self, cur_x, cur_y):
        all_stick_ball_ids = [sorted([x.start_ball_id, x.end_ball_id]) for x in self.data.sticks]
        # check_click in not virtual
        i = 0
        while i < len(self.data.balls):
            ix = i
            if self.data.balls[ix].check_click(cur_x, cur_y):
                if self.data.last_ball < 0:
                    self.data.last_ball = ix
                else:
                    if self.data.last_ball != ix:
                        result = sorted([self.data.last_ball, ix])
                        if all_stick_ball_ids.count(result) == 0:
                            self.data.new_stick(ix)
                        else:
                            ix_stick = all_stick_ball_ids.index(result)
                            self.data.remove_stick(ix_stick)
                    self.data.last_ball = -1
                return True
            i += 1
        return False

class DigitalTestTool(ToolsBase):
    ix = 0

    def get_name(self):
        return 'DigitalTest'

    def on_mouse_wheel_up(self, cur_x, cur_y):
        """

        :param cur_x: float
        :param cur_y: float
        :return bool
        """
        if self.ix > -1:
            self.ix -= 1
        return True

    def on_mouse_wheel_down(self, cur_x, cur_y):
        """

        :param cur_x: float
        :param cur_y: float
        :return bool
        """
        if self.ix < 50:
            self.ix += 1
        return True

    def draw(self, cur_x, cur_y):
        # type: (float, float) -> ()
        """

        :param cur_y: float
        :param cur_x: float
        """
        return self.scene.i_push_step().d_push_digital_size() \
            .d_set_digital_size(10).i_move_to(cur_x, cur_y)._draw_digital([self.ix]).d_draw_tex(str(self.ix)) \
            .i_pop_step().d_pop_digital_size()
