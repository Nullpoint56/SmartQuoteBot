from common.interfaces.service_manager import BootableService

class ServiceManager:
    """Manager for booting, shutting down, and managing multiple services."""

    def __init__(self) -> None:
        self.services: list[BootableService] = []

    def add_service(self, service: BootableService) -> None:
        """Register a service to be managed."""
        self.services.append(service)

    def boot_all(self) -> None:
        """Boot all registered services."""
        for service in self.services:
            service.boot()

    def shutdown_all(self) -> None:
        """Shutdown all registered services (in reverse order)."""
        for service in reversed(self.services):
            service.shutdown()

    def shutdown_service(self, service: BootableService) -> None:
        """Shutdown a specific service."""
        if service in self.services:
            service.shutdown()

    def boot_service(self, service: BootableService) -> None:
        """Boot a specific service."""
        if service in self.services:
            service.boot()

    def restart_service(self, service: BootableService) -> None:
        """Gracefully restart a specific service."""
        if service in self.services:
            service.shutdown()
            service.boot()

    def restart_services(self, services: list[BootableService]) -> None:
        """Gracefully restart multiple services."""
        for service in services:
            if service in self.services:
                service.shutdown()

        for service in services:
            if service in self.services:
                service.boot()
