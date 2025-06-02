from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def log(self, message):
        pass

    @abstractmethod
    def error(self, message):
        pass

    def debug(self, message):
        pass
