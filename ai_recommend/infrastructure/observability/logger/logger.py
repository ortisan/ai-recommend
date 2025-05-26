from abc import ABC, abstractmethod


class ILogger(ABC):
    @abstractmethod
    def log(self, message):
        pass

    @abstractmethod
    def error(self, message):
        pass

    def debug(self, message):
        pass
