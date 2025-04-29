from common.interfaces.service_manager import BootableService
from common.utils.sentry import setup_sentry
from service_manager import ServiceManager
from embedding_service.service import EmbeddingService


def setup_services(service_manager: ServiceManager) -> dict[str, BootableService]:
    """Instantiate and register all services. Return a name->service map."""
    services = {}

    embedding_service = EmbeddingService()

    services["embedding_service"] = embedding_service

    for service in services.values():
        service_manager.add_service(service)

    return services


def print_commands(commands: dict) -> None:
    print("\nSmartQuoteBot Service Manager CLI")
    print("---------------------------------")
    print("Available commands:")
    for cmd in commands.keys():
        print(f" - {cmd}")
    print(" - boot [service_name]")
    print(" - shutdown [service_name]")
    print(" - restart [service_name]")
    print(" - exit")


def handle_service_action(service_manager: ServiceManager, action: str, name: str, service_map: dict) -> None:
    service = service_map.get(name)
    if not service:
        print(f"Service '{name}' not found.")
        return

    match action:
        case "boot":
            service_manager.boot_service(service)
            print(f"Booted service: {name}")
        case "shutdown":
            service_manager.shutdown_service(service)
            print(f"Shutdown service: {name}")
        case "restart":
            service_manager.restart_service(service)
            print(f"Restarted service: {name}")


def handle_status(service_map: dict) -> None:
    print("\nService Status:")
    for name, service in service_map.items():
        healthy = service.health_check()
        status = "Healthy" if healthy else "Unhealthy"
        print(f" - {name}: {status}")


def handle_list(service_map: dict) -> None:
    print("\nRegistered Services:")
    for name in service_map.keys():
        print(f" - {name}")


def cli_loop(service_manager: ServiceManager, service_map: dict[str, BootableService]) -> None:  # noqa
    """Interactive CLI loop to manage services."""

    # Mapping simple commands to handlers
    commands = {
        "boot_all": lambda: (service_manager.boot_all(), print("All services booted.")),
        "shutdown_all": lambda: (service_manager.shutdown_all(), print("All services shut down.")),
        "restart_all": lambda: (
            service_manager.shutdown_all(), service_manager.boot_all(), print("All services restarted.")),
        "status": handle_status,
        "list": handle_list,
    }

    print_commands(commands)

    while True:
        cmd = input("\n> ").strip().lower()

        if cmd == "exit":
            print("Exiting...")
            break
        elif cmd.startswith(("boot ", "shutdown ", "restart ")):
            action, name = cmd.split(maxsplit=1)
            handle_service_action(service_manager, action, name, service_map)
        elif cmd in commands:
            commands[cmd]()
        else:
            print("Unknown command. Type 'list' to see available services.")


def main():
    setup_sentry()

    service_manager = ServiceManager()
    service_map = setup_services(service_manager)

    try:
        service_manager.boot_all()
        cli_loop(service_manager, service_map)

    finally:
        service_manager.shutdown_all()


if __name__ == "__main__":
    main()
