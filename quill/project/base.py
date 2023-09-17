from abc import ABC, abstractmethod
from typing import Mapping

from quill.bot import BaseBot, BotFactory
from quill.core.config import Config
from quill.core.types import ProjectTypes, SingletonMeta
from quill.server import BaseServer, ServerFactory

from quill.core.pretty import Pretty

pretty = Pretty()

class BaseProject(ABC):
    def __init__(self, config: Config) -> None:
        
        self.name: str = None
        """Name of the project"""

        self.project_root: str = None
        """Root directory of the project"""

        self.project_type: str = None
        """Type of the project"""

        self.bot: BaseBot = None
        """Bot instance of the project"""

        self.server: BaseServer = None
        """Server instance of the project"""

        self.init(config=config)

        self.bot = BotFactory().create_bot(config)
        self.server = ServerFactory().create_server(config)

    @abstractmethod
    def init(self, config: Config):
        """Initializes a project."""

    @abstractmethod
    def build(self):
        """Builds a project"""

    @abstractmethod
    def deploy(self):
        """Deploys a project"""

    @abstractmethod
    def test(self):
        """Tests a project"""

    @abstractmethod
    def serve(self):
        """Serves a project"""


class ProjectFactory(metaclass=SingletonMeta):
    """Factory for creating project instances."""

    def __init__(self) -> None:
        self.project_map: Mapping[str, BaseProject] = {}
        """Mapping of model types to project class."""

    def register_project(self, project_type: str, project: BaseProject) -> None:
        """Registers an project class with the given model project_type."""
        self.project_map[project_type] = project

    def create_project(self, config: Config) -> BaseProject:
        """Creates a project instance with the given name and config."""
        project_config = config.project
        project_type = project_config.project_type
        return self.project_map[project_type](config)
