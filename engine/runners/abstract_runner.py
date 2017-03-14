# runner.py

import abc


class AbstractRunner(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def run(self, filename):
        """Execute the given file and return its output."""
