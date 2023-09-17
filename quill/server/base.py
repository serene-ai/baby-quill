from abc import ABC, abstractmethod
from typing import Mapping, Optional

from quill.core.config import Config
from quill.core.types import ServerTypes, SingletonMeta


class BaseServer(ABC):
    """Base class for Quill servers."""

    def __init__(self) -> None:
        self.name: ServerTypes = None
        self.init()
        """Name of the server."""
    
    @abstractmethod
    def init(self):
        """Initializes the server."""

    @abstractmethod
    def run(self, port: Optional[int]):
        """Runs the server."""


class ServerFactory(metaclass=SingletonMeta):
    """Factory for creating server instances."""

    def __init__(self) -> None:
        self.server_map: Mapping[str, BaseServer] = {}
        """Mapping of model names to server class."""

    def register_server(self, name: str, server: BaseServer) -> None:
        """Registers a server class with the given server type."""
        self.server_map[name] = server

    def create_server(self, config: Config) -> BaseServer:
        """Creates a server instance with the given model name and config."""
        server_config = config.server
        name = server_config.name
        return self.server_map[name]()
