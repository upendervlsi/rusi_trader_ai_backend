from abc import ABC
from abc import abstractmethod


class BaseVerifier(ABC):

    @abstractmethod
    def verify(self, snapshot):

        pass
