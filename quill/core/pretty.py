from rich.console import Console
from rich.traceback import install


install()


class Pretty:
    _instance = None

    def __new__(cls: 'Pretty'):
        if cls._instance is None:
            cls._instance = super(Pretty, cls).__new__(cls)
            cls._instance.console = Console()
        return cls._instance

    def error(self, error_type: str, message: str, terminate: bool = False):
        self.console.print(f"[bold red]{error_type}: [/bold red]{message}")
        if terminate:
            exit(1)

    def info(self, message: str):
        self.console.print(f"[bold cyan]{message}[/bold cyan]")

    def success(self, message: str):
        self.console.print(f"[bold green]{message}[/bold green]")

    def message(self, message: str):
        self.console.print(f"{message}")
