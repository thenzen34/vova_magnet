from base_classes import StreamData
from Scene.stream_io import StreamIO


class Stick(StreamData):
    def load_from_stream(self, stream):
        reader = StreamIO(stream)
        self.start_ball_id = reader.read_int16()
        self.end_ball_id = reader.read_int16()

    def save_to_stream(self, stream):
        reader = StreamIO(stream)
        reader.write_int16(self.start_ball_id)
        reader.write_int16(self.end_ball_id)

    def __init__(self, start_ball_id, end_ball_id):
        """

        :type end_ball_id: int
        :type start_ball_id: int
        """
        self.start_ball_id = start_ball_id
        self.end_ball_id = end_ball_id

    def __str__(self):
        return '{0} -> {1}'.format(self.start_ball_id, self.end_ball_id)
