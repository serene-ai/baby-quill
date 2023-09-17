import typer
from typing import Optional
from typing_extensions import Annotated

from quill.core.config import Config
from quill.project import ProjectFactory
from quill.core.pretty import Pretty
import os
from pathlib import Path
from quill.core.utils import load_module, load_dependent_modules

cli = typer.Typer()
pretty = Pretty()


@cli.command()
def init():
    """
    Initializes a new Quill project.
    """
    config = Config.new()
    project = ProjectFactory().create_project(config=config)


@cli.command()
def new(name: Annotated[Path, typer.Argument(help="Project name")]):
    """
    Creates a new Quill project.
    """

    if os.path.exists(name):
        pretty.error(
            error_type="ProjectAlreadyExists",
            message=f"Project {name} already exists.",
            terminate=True,
        )
    config = Config.new(project_name=name)


# ✅
@cli.command()
def serve(file_name: Annotated[Optional[str], typer.Argument()] = None):
    """
    Serves a Quill project.
    """
    if file_name:
        # module = load_module(file_name=file_name)
        dependent_modules = load_dependent_modules(file_path=file_name)
    config = Config.init(file_name=file_name)
    project = ProjectFactory().create_project(config=config)
    pretty.message(f"Running {project.name}...")
    project.serve()


if __name__ == "__main__":
    typer.run(cli)
