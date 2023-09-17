from abc import ABC, abstractmethod
from typing import Mapping

from quill.core.config import Config
from quill.core.types import BotTypes, SingletonMeta
from quill.llm import BaseLLM, LLMFactory


class BaseBot(ABC):
    """Base class for all bots."""

    def __init__(self, config: Config) -> None:
        self.name: str = None
        """Name of this bot."""

        self.llm: BaseLLM = None
        """LLM instance this bot is associated with."""

        self.init(config=config)

        self.llm = LLMFactory().create_llm(config)

    def get_llm(self) -> BaseLLM:
        """Returns the LLM instance this bot is associated with."""
        return self.llm

    def get_response(self, *args, **kwargs):
        """Returns a response from the LLM instance this bot is associated with."""
        llm = self.get_llm()
        return llm.generate(*args, **kwargs)

    @abstractmethod
    def init(self, config: Config):
        """Initializes the bot with the given config."""


class BotFactory(metaclass=SingletonMeta):
    """Factory for creating bot instances."""

    def __init__(self) -> None:
        self.bot_map: Mapping[str, BaseBot] = {}
        """Mapping of model names to bot class."""

    def register_bot(self, name: str, bot: BaseBot) -> None:
        """Registers an bot class with the given model name."""
        self.bot_map[name] = bot

    def create_bot(self, config: Config) -> BaseBot:
        """Creates a bot instance with the given name and config."""

        bot_config = config.bot
        name = bot_config.name

        return self.bot_map[name](config)
