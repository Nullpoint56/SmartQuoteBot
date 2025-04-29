from abc import ABC, abstractmethod

class LazyLoadable(ABC):
    """Abstract Base Class for resources that support lazy initialization."""

    @abstractmethod
    def boot(self) -> None:
        """Load heavy resources, connect, etc."""
        ...

    @abstractmethod
    def is_ready(self) -> bool:
        """Return True if the resource is initialized and ready."""
        ...
