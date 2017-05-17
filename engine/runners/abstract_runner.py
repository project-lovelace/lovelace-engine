from abc import ABCMeta, abstractmethod


class AbstractRunner(metaclass=ABCMeta):

    @abstractmethod
    def run(self, filename, input_str):
        """Execute the given file and return its output."""
