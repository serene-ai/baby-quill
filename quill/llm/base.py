from abc import ABC, abstractmethod
from typing import Mapping

from quill.core.config import Config
from quill.core.types import LLMTypes, SingletonMeta


class BaseLLM(ABC):
    """Base class for LLM models."""

    def __init__(self) -> None:
        self.instance = None
        """Instance of the LLM model."""

        self.model_name: str = None
        """Name of the LLM model."""

        self.init()

    def get_instance(self):
        """Returns the instance of the LLM model."""
        return self.instance

    @abstractmethod
    def init(self, config: Config):
        """Initializes the LLM model with the given config."""

    @abstractmethod
    def generate(self, *args, **kwargs):
        """Generates a response from the LLM model."""


class LLMFactory(metaclass=SingletonMeta):
    """Factory for creating LLM instances."""

    def __init__(self) -> None:
        self.llm_map: Mapping[str, BaseLLM] = {}
        """Mapping of model names to LLM class."""

    def register_llm(self, model_name: str, llm: BaseLLM) -> None:
        """Registers an LLM class with the given model name."""
        self.llm_map[model_name] = llm

    def create_llm(self, config: Config) -> BaseLLM:
        """Creates an LLM instance with the given model name and config."""

        llm_config = config.llm
        model_name = llm_config.model_name

        return self.llm_map[model_name]()
