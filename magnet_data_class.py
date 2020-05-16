from math import *

from ball_class import Ball
from Scene.stream_io import StreamIO
from stick_class import Stick


def find_left_b(arr, search_val):
    i = 0
    start_ix = 0
    end_ix = len(arr) - 1
    if end_ix < 0:
        return 0
    elif end_ix == 0:
        return 0 if arr[0][1] > search_val else 1
    while True:
        i += 1
        cur_ix = (start_ix + end_ix + 1) // 2

        last_iter = (start_ix, end_ix, cur_ix)
        ix, val = arr[cur_ix]
        if val >= search_val:
            end_ix = cur_ix
        else:
            start_ix = cur_ix

        # print([cur_ix, start_ix, end_ix], arr[cur_ix])

        cur_iter = (start_ix, end_ix, cur_ix)
        if last_iter == cur_iter:
            # print(i, end='-')
            while arr[start_ix][1] < search_val and end_ix > start_ix:
                start_ix += 1
                i += 1
            # print(i, end=' ')
            return start_ix


def find_right_b(arr, search_val):
    i = 0
    start_ix = 0
    end_ix = len(arr) - 1
    if end_ix < 0:
        return 0
    elif end_ix == 0:
        return 0 if arr[0][1] < search_val else 1
    while True:
        i += 1
        cur_ix = (start_ix + end_ix + 1) // 2
        last_iter = (start_ix, end_ix, cur_ix)

        ix, val = arr[cur_ix]
        if val > search_val:
            end_ix = cur_ix
        else:
            start_ix = cur_ix
        # print([cur_ix, start_ix, end_ix], arr[cur_ix])

        cur_iter = (start_ix, end_ix, cur_ix)
        if last_iter == cur_iter:
            # print(i, end='-')
            while arr[end_ix][1] > search_val and end_ix > start_ix:
                end_ix -= 1
                i += 1
            # print(i, end=' ')
            return end_ix


# типа модель данных
class MagnetsData:
    def reset_system(self):
        self.balls.clear()
        self.virtual.clear()
        self.not_virtual.clear()
        self.sticks.clear()

        self.last_ball = -1
        self.all_balls_r.clear()
        return self

    def save_system_to_stream(self, stream):
        writer = StreamIO(stream)

        length = len(self.balls)
        writer.write_int16(length)
        while length > 0:
            self.balls[length - 1].save_to_stream(stream)
            length -= 1

        length = len(self.sticks)
        writer.write_int16(length)
        while length > 0:
            self.sticks[length - 1].save_to_stream(stream)
            length -= 1

    def clear_virtual_ball(self):
        del_ix = len(self.virtual)
        while del_ix > 0:
            self.remove_ball(self.virtual[del_ix - 1])
            self.virtual.pop(del_ix - 1)
            del_ix -= 1

    def load_system_from_stream(self, stream):
        reader = StreamIO(stream)

        length = reader.read_int16()
        while length > 0:
            ix = length - 1
            ball = Ball(0, 0, 0, 0, 0)
            ball.load_from_stream(stream)
            if ball.virtual:
                self.virtual.append(ix)
            else:
                self.not_virtual.append(ix)
            self.balls.insert(0, ball)
            self.all_balls_r.insert(0, (ix, ball.get_r()))

            length -= 1

        self.all_balls_r.sort(key=lambda t: t[1])  # сортируем по удаленности

        length = reader.read_int16()
        while length > 0:
            stick = Stick(0, 0)
            stick.load_from_stream(stream)
            self.sticks.insert(0, stick)
            length -= 1

        self.clear_virtual_ball()

    balls = [Ball(0, 0, 0, 0, 0) for _ in range(0)]  # все шары
    virtual = []  # индексы виртуальных шаров
    not_virtual = []  # индексы не виртуальных шаров
    sticks = [Stick(-1, -1) for _ in range(0)]  # все палки

    last_ball = -1  # последний выбранный шар (для создания палки, ..)

    def new_ball(self, x, y, length, r):
        ix = len(self.balls)
        ball = Ball(x, y, length, r, ix)
        ball.virtual = False
        self.not_virtual.append(ix)
        self.update_r(ball)
        self.balls.append(ball)
        return ball

    def update_r(self, ball):
        """

        :param ball: Ball
        """
        r = ball.get_r()
        ix = find_left_b(self.all_balls_r, r)
        if ix + 1 == len(self.all_balls_r):
            self.all_balls_r.append((ball.s_id, r))
        else:
            self.all_balls_r.insert(ix, (ball.s_id, r))

    def set_ball_not_virtual(self, ix):
        """

        :param ix: int
        """
        new_ix = max(self.not_virtual) + 1
        ball = self.balls[ix]

        self.virtual.remove(ix)
        ball.set_not_virtual()

        self.clear_virtual_ball()
        self.not_virtual.append(new_ix)

        self.balls[self.last_ball].add_parent(new_ix)

    def new_stick(self, ix):
        """

        :param ix: int
        """
        # todo save sorted, test
        self.sticks.append(Stick(*sorted([self.last_ball, ix])))
        # print('add stick')

    def rename_ball(self, ball_id, new_ix):
        """

        :param new_ix: int
        :param ball_id: int
        """
        if ball_id == new_ix:
            return False
        # переименовать себя, у родителей, у стиков, у списков
        ball = self.balls[ball_id]
        for parent_id in ball.parents_id:
            parent = self.balls[parent_id]
            parent.parents_id.remove(ball_id)
            parent.parents_id.append(new_ix)
        ball.s_id = new_ix
        self.balls[new_ix] = ball
        for stick in self.sticks:
            if stick.start_ball_id == ball_id:
                stick.start_ball_id = new_ix
            if stick.end_ball_id == ball_id:
                stick.end_ball_id = new_ix

        if self.virtual.count(ball_id):
            self.virtual.remove(ball_id)
            self.virtual.append(new_ix)
        if self.not_virtual.count(ball_id):
            self.not_virtual.remove(ball_id)
            self.not_virtual.append(new_ix)

        ix = self.all_balls_r.index((ball_id, ball.get_r()))
        self.all_balls_r[ix] = (ball.s_id, ball.get_r())

        return True

    def remove_ball(self, ix):
        if len(self.balls) < 2:
            return False
        # удалить стики, связи у родителей, фикс очереди
        ball = self.balls[ix]
        j = 0
        while j < len(self.sticks):
            stick = self.sticks[j]
            if stick.end_ball_id == ix or stick.start_ball_id == ix:
                self.remove_stick(j)
                continue
            j += 1
        for parent_id in ball.parents_id:
            parent = self.balls[parent_id]
            parent.parents_id.remove(ix)
        old_id = len(self.balls) - 1
        # todo remove virtual ?
        if self.not_virtual.count(ix):
            self.not_virtual.remove(ix)

        ix_del = self.all_balls_r.index((ix, ball.get_r()))
        self.all_balls_r.pop(ix_del)

        self.rename_ball(old_id, ix)
        self.balls.pop(old_id)
        # print('remove ball')

        # print(self.all_balls_r)

    def remove_stick(self, ix):
        """

                :param ix: int
                """
        self.sticks.pop(ix)
        # print('remove stick')

    def add_to_parents(self, ball_id, possible_parents):
        """

        :type ball_id: int
        :type possible_parents: []
        :return []
        """
        cur_ball = self.balls[ball_id]
        for result, select_ball_ix in possible_parents:
            if select_ball_ix >= 0:
                # print('add_to_parents=', select_ball_ix)
                ix = select_ball_ix
                ball = self.balls[ix]
                ball.add_parent(cur_ball.s_id)
                cur_ball.parents_id.append(ix)

    def get_all_parents_ball(self, ball_id, get_move_xy_function):
        """

        :type ball_id: int
        :type get_move_xy_function: Callable[float, float]
        :return []
        """
        cur_ball = self.balls[ball_id]

        # add 12 ball
        angles = [0, 60, 90, 120, 180, 240, 270, 300]
        angles += [30, 150, 210, 330]

        # angles += [72, 144, 216, 288]
        result = []
        for angle in angles:
            x, y = get_move_xy_function(angle, cur_ball.length)
            r = sqrt(pow(x + cur_ball.x, 2) + pow(y + cur_ball.y, 2))
            start_ix = find_left_b(self.all_balls_r, r - cur_ball.r)
            end_ix = find_right_b(self.all_balls_r, r + cur_ball.r)
            select_ball_ix = -1
            for i in range(start_ix, end_ix + 1):
                # print('test ', i)
                ix = self.all_balls_r[i][0]
                # если шары не в одной четверти то пропускаем
                '''
                if cur_ball.x * self.balls[ix].x < 0 or cur_ball.y * self.balls[ix].y < 0:
                    continue
                '''
                if self.balls[ix].check_click(x + cur_ball.x, y + cur_ball.y):
                    # если есть такой шар в который мы попадаем используем его
                    select_ball_ix = ix
                    break
            result.append(((x + cur_ball.x, y + cur_ball.y), select_ball_ix))

        return result

    all_balls_r = [(0, 0.) for _ in range(0)]

    def get_virtual_balls(self, ball_id, get_move_xy_function):
        """

        :type get_move_xy_function: Callable[float, float]
        :type ball_id: int
        :return []
        """

        cur_ball = self.balls[ball_id]
        # add new virtual check not duplicate
        # all_balls_xy = [tuple(trunc(x) // cur_ball.r for x in x.get_xy()) for x in self.balls]  # if x.enable

        # ищем по радиальному удалению
        # 1. строим таблицу удаленности (дополняем ее когда создаем новый шар)
        # 2. log2 ищем старт и конец индекса текущей удаленности шара +- r

        all_possible_virtual = []

        # print(self.all_balls_r)
        # смотрим на всех родительские шары
        for result, select_ball_ix in self.get_all_parents_ball(ball_id, get_move_xy_function):
            # иначе создаем новый
            if select_ball_ix < 0:
                ix = len(self.balls)
                all_possible_virtual.append(ix)
                ball = Ball(*result, cur_ball.length, cur_ball.r, ix)
                self.update_r(ball)
                self.balls.append(ball)
                # print('get_virtual_balls add_to_parents=', select_ball_ix)
                self.add_to_parents(ix, self.get_all_parents_ball(ix, get_move_xy_function))
            else:
                # print('get_virtual_balls=', select_ball_ix)
                ix = select_ball_ix
                ball = self.balls[ix]
                if ball.virtual:
                    if not ball.enable:
                        ball.enable = True
                    # print('add parents', ix, cur_ball.s_id)
                    ball.add_parent(cur_ball.s_id)
                    cur_ball.parents_id.append(ix)

        # print('add {0} balls'.format(len(all_possible_virtual)))
        return all_possible_virtual
