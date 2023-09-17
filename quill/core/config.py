import os
from abc import ABC
from enum import Enum
from pathlib import Path

import toml
import typer
from pydantic import BaseModel, Field, ValidationError

from quill.core.pretty import Pretty
from quill.core.types import BotTypes, LLMTypes, ProjectTypes, ServerTypes

pretty = Pretty()


class BaseConfig(ABC):
    protected_namespaces = ()

    @classmethod
    def collect(cls):
        """
        Iteratively collects input from the user and returns an instance of the model.
        Returns: An instance of the model.
        """

        input_data = {}

        # Iterate through the model's fields
        for field_name, field_info in cls.__annotations__.items():
            if issubclass(field_info, BaseConfig):
                # If the field is an instance of BaseConfig, call its collect method
                pretty.info(f"{field_name.capitalize()}")
                value = field_info.collect()
                if value is None:
                    pretty.error(
                        error_type="ValidationError",
                        message=f"Couldn't collect {field_name}.",
                        terminate=True,
                    )
                input_data[field_name] = value
            else:
                while True:
                    try:
                        options = None
                        if issubclass(field_info, Enum):
                            options = field_info.get_options()
                        value = typer.prompt(
                            f"{field_name.capitalize()}{' (Choices ' + ', '.join(options) + ')' if options else ''}: ",
                            prompt_suffix="",
                            default=cls.__dict__["model_fields"][
                                field_name
                            ].default,  # get the default value from the model
                        )

                        # Validate and convert the input to the expected field type
                        input_data[field_name] = field_info(value)
                        break  # Input is valid, exit the loop
                    except ValueError:
                        pretty.error(
                            error_type="ValueError",
                            message=f"Invalid input for {field_name}. Please enter a valid {field_name}.",
                            terminate=True,
                        )

        try:
            # Create an instance of the model with the collected data
            instance = cls(**input_data)
            cls.model_validate(instance)
            return instance  # Return the instance after successful validation
        except ValidationError as e:
            pretty.error(
                error_type="ValidationError",
                message=f"Validation failed: {e}",
                terminate=True,
            )
            return None


class ProjectConfig(BaseModel, BaseConfig):
    name: str = Field(
        description="Name of the project", default=os.getcwd().split("/")[-1]
    )
    project_type: ProjectTypes = Field(
        description="Type of the project", default=ProjectTypes.default()
    )
    project_root: Path = Field(
        description="Root directory of the project", default=os.path.curdir
    )


class BotConfig(BaseModel, BaseConfig):
    name: BotTypes = Field(description="Name of the bot", default=BotTypes.default())


class LLMConfig(BaseModel, BaseConfig):
    model_name: LLMTypes = Field(
        description="Name of the LLM model", default=LLMTypes.default()
    )

    class Config:
        # Set protected_namespaces to an empty tuple to avoid naming conflicts
        protected_namespaces = ()


class ServerConfig(BaseModel, BaseConfig):
    name: ServerTypes = Field(
        description="Name of the server", default=ServerTypes.default()
    )


class Config(BaseModel, BaseConfig):
    project: ProjectConfig = Field(..., description="Project config")
    bot: BotConfig = Field(..., description="Bot config")
    llm: LLMConfig = Field(..., description="LLM config")
    server: ServerConfig = Field(..., description="Server config")

    @classmethod
    def init(cls, file_name: str = None):
        """
        Initializes a new project.
        
        Args:
            file_name: Name of the server file.
        
        """
        if not os.path.exists("quill.toml"):
            pretty.error(
                error_type="ConfigError",
                message="No quill.toml file found.",
                terminate=True,
            )

        if file_name and not os.path.exists(file_name):
            pretty.error(
                error_type="ConfigError",
                message=f"No {file_name} file found.",
                terminate=True,
            )

        with open("quill.toml", "r") as f:
            quill_toml = toml.load(f=f)

        config = Config.model_construct(**quill_toml)
        config.llm = LLMConfig.model_construct(**config.llm)
        config.server = ServerConfig.model_construct(**config.server)
        config.bot = BotConfig.model_construct(**config.bot)
        config.project = ProjectConfig.model_construct(**config.project)

        try:
            cls.model_validate(config)
        except ValidationError as e:
            pretty.error(error_type="ValidationError", message=f"{e}", terminate=True)

        return config

    @classmethod
    def new(cls, project_name: str = None):
        """
        Builds the config for a new project.

        Args:
            project_name: Name of the project.
        """

        if project_name:
            try:
                os.makedirs(project_name)
            except OSError:
                pretty.error(
                    error_type="ConfigError",
                    message="Failed to create project directory.",
                    terminate=True,
                )

        if os.path.isfile("quill.toml"):
            pretty.error(
                error_type="ConfigError",
                message="A quill.toml file already exists in this directory.",
                terminate=True,
            )
        config = cls.collect()
        data = config.model_dump(mode="json")
        quill_toml_file_path = os.path.join(config.project.project_root, "quill.toml")
        with open(quill_toml_file_path, "w") as f:
            toml.dump(data, f)

        return config
