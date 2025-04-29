from abc import ABC, abstractmethod

class BootableService(ABC):
    """Abstract Base Class for services that can be booted and shut down."""

    @abstractmethod
    def boot(self) -> None:
        """Boot the service (connect, load models, etc.)."""
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the service (disconnect, cleanup, etc.)."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the service is healthy, False otherwise."""
        ...
