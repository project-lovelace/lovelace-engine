from abc import ABCMeta, abstractmethod


class AbstractRunner(metaclass=ABCMeta):

    @abstractmethod
    def run(self, container_name, filename, input_str):
        """Execute the given file using input_str as input through stdin and return the program's output."""
