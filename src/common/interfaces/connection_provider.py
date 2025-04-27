# src/common/interfaces/connection_provider.py

from typing import Protocol, Any


class ConnectionProvider(Protocol):
    """Protocol for providing a database or storage connection."""

    def connect(self) -> Any:
        """Establish and return a connection."""
        ...

    def shutdown(self) -> None:
        """Close any resources if needed."""
        ...
