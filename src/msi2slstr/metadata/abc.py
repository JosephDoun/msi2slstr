from abc import ABCMeta, abstractmethod


class Metadata(metaclass=ABCMeta):
    """
    Abstract class of a Metadata object.
    """
    @property
    @abstractmethod
    def domain(self) -> str: ...
    @property
    @abstractmethod
    def content(self) -> dict: ...
