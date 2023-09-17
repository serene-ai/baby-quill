import os
import click
import importlib.util
import inspect
import subprocess
import urllib.parse
import pkgutil
from pathlib import Path


def load_module(file_name: Path | None):
    if file_name:
        _directory = os.getcwd()
        spec = importlib.util.spec_from_file_location(_directory, file_name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # modules = load_dependent_modules(file_path=file_name)


def load_dependent_modules(file_path):
    # Get the directory containing the specified file
    file_path = os.path.join(os.getcwd(), file_path)
    directory = os.path.dirname(file_path)

    # Create a list to store loaded modules
    loaded_modules = []

    # Walk through the directory and load all Python modules
    for loader, module_name, is_pkg in pkgutil.walk_packages([directory]):
        if not is_pkg:
            module_path = os.path.join(directory, f"{module_name}.py")

            # Check if the module file exists
            if os.path.exists(module_path):
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                loaded_modules.append(module)

    return loaded_modules
