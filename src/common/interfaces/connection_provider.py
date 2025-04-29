from abc import ABC, abstractmethod
from typing import Any

class ConnectionProvider(ABC):
    """Abstract Base Class for providing a database or storage connection."""

    @abstractmethod
    def connect(self) -> Any:
        """Establish and return a connection."""
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Close any resources if needed."""
        ...
