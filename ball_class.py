import math
from math import *

from base_classes import StreamData
from Scene.stream_io import StreamIO


class Ball(StreamData):
    def load_from_stream(self, stream):
        reader = StreamIO(stream)
        self.s_id = reader.read_int16()

        length = reader.read_int16()
        while length > 0:
            self.parents_id.insert(0, reader.read_int16())
            length -= 1

        self.r = reader.read_double()
        self.length = reader.read_double()
        self.virtual = reader.read_boolean()
        self.x = reader.read_double()
        self.y = reader.read_double()
        self.enable = reader.read_boolean()

    def save_to_stream(self, stream):
        reader = StreamIO(stream)
        reader.write_int16(self.s_id)

        length = len(self.parents_id)
        reader.write_int16(length)
        while length > 0:
            reader.write_int16(self.parents_id[length - 1])
            length -= 1

        reader.write_double(self.r)
        reader.write_double(self.length)
        reader.write_boolean(self.virtual)
        reader.write_double(self.x)
        reader.write_double(self.y)
        reader.write_boolean(self.enable)

    def __init__(self, x, y, length, r, s_id):
        """

        :type s_id: int
        :type r: float
        :type length: float
        :type y: float
        :type x: float
        """
        self.s_id = s_id
        self.parents_id = [0 for _ in range(0)]
        self.r = r
        self.length = length
        self.virtual = True
        self.x = x
        self.y = y
        # TODO remove enable
        self.enable = True

    def disable(self):
        self.enable = False

    def add_parent(self, parent_id):
        if self.parents_id.count(parent_id) == 0:
            self.parents_id.append(parent_id)
        else:
            # print('ups')
            pass

    def __str__(self):
        return '{0}x{1}={2} ({3} | {4})'.format(self.x, self.y, self.virtual, self.r, self.length)

    def get_xy(self):
        return self.x, self.y

    def get_r(self):
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))

    def set_not_virtual(self):
        self.virtual = False

    def check_click(self, x, y):
        """

        :type y: float
        :type x: float
        """
        if not self.enable:
            return False
        length = sqrt(pow(x - self.x, 2) + pow(y - self.y, 2))
        return length < self.r
