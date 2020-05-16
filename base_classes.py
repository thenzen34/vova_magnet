from abc import ABC, abstractmethod


class StreamData(ABC):

    @abstractmethod
    def load_from_stream(self, stream):
        pass

    @abstractmethod
    def save_to_stream(self, stream):
        pass
