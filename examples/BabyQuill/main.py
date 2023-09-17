import os
import shutil
import subprocess
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from openai import ChatCompletion

from quill.bot import BaseBot, BotFactory
from quill.core.config import Config
from quill.core.pretty import Pretty
from quill.core.types import BotTypes, LLMTypes, ProjectTypes, ServerTypes
from quill.core.utils import QUILL_DIR
from quill.llm import BaseLLM, LLMFactory
from quill.project import BaseProject, ProjectFactory
from quill.server import BaseServer, ServerFactory

pretty = Pretty()


BotTypes.extend("BabyQuill", "baby-quill")
LLMTypes.extend("Gpt3_5Turbo", "gpt-3.5-turbo")
ProjectTypes.extend("StaticWebsite", "static-website")
ServerTypes.extend("StaticWebsiteServer", "static-website-server")


class Gpt3_5Turbo(BaseLLM):
    """gpt 3.5 turbo"""

    def init(self):
        self.model_name = LLMTypes.Gpt3_5Turbo.value

    def generate(self, *args, **kwargs):
        """Generates a response from the LLM model."""
        messages = kwargs.get("messages", None)
        return ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)


class BabyQuill(BaseBot):
    """🔮 Baby Quill is the infant version of next generation code genies"""

    def init(self, config: Config):
        self.name = BotTypes.BabyQuill.value

    def generate(self, *args, **kwargs):
        """Generates a response from the LLM model."""
        return self.get_llm().generate(*args, **kwargs)


class StaticWebsiteServer(BaseServer):
    """Serves static websites"""

    def init(self, config: Config):
        self.app = FastAPI()

        quill_dist = os.path.join(QUILL_DIR, "dist")

        current_dir = os.getcwd()
        print(current_dir)
        project_dist = os.path.join(current_dir, "dist")

        self.mount(app=self.create_app(quill_dist), path="/", name="quill")
        self.mount(app=self.create_app(project_dist), path=f"/project", name=f"{config.project.name.lower()}")

    def create_app(self, path):
        sub_app = FastAPI()
        pretty.info(f"Creating app for {path}")
        sub_app.mount("/static", StaticFiles(directory=f"{path}/static"), name="static")

        @sub_app.get("/", response_class=HTMLResponse)
        async def root():
            with open(f"{path}/index.html") as f:
                return f.read()

        return sub_app

    def mount(self, app, path, name):
        self.app.mount(path=path, app=app, name=name)

    
    def run(self, port: int = 4455):
        uvicorn.run(self.app, host="localhost", port=port)



        
        


class StaticWebsite(BaseProject):
    """Build static websites with Quill"""

    def init(self, config: Config):
        project_config = config.project
        self.name = project_config.name
        self.project_type = ProjectTypes.StaticWebsite.value
        self.project_root = project_config.project_root

    def build(self):
        project_root = os.getcwd() if self.project_root == "." else self.project_root
        dist_root = os.path.join(project_root, "dist")
        static_root = os.path.join(dist_root, "static")

        if os.path.exists(static_root):
            shutil.rmtree(dist_root)
            pretty.info(f"Deleted {dist_root}")

        os.makedirs(static_root)

        self._minify_files()

        return (dist_root, static_root)

        # files available at "dist/index.html" and "dist/static/*"

    def _minify_files(self):
        """Minifies files in the static directory"""
        dist_root = "dist"
        static_root = os.path.join(dist_root, "static")

        try:
            # install dependencies
            dependencies = ["css-minify", "html-minifier", "uglify-js"]

            install_dependencies_cmd = ["npm", "install", *dependencies, "-g"]
            subprocess.run(install_dependencies_cmd, check=True)

            # Minify HTML
            html_minify_cmd = [
                "npx",
                "html-minifier",
                "--file-ext",
                "html",
                "--input-dir",
                ".",
                "--output-dir",
                dist_root,
                "--collapse-whitespace",
                "--minify-css",
                "--minify-js",
            ]
            subprocess.run(html_minify_cmd, check=True)

            js_files = filter(lambda x: x.endswith(".js"), os.listdir("."))
            # Minify JS
            js_minify_cmd = [
                "npx",
                "uglify-js",
                *js_files,
                "-c",
                "-m",
                "-o",
                os.path.join(static_root, "index.js"),
            ]
            subprocess.run(js_minify_cmd, check=True)

            # Minify CSS
            css_minify_cmd = [
                "npx",
                "css-minify",
                "-d",
                ".",
                "-o",
                static_root,
            ]
            subprocess.run(css_minify_cmd, check=True)

        except subprocess.CalledProcessError as e:
            pretty.error(
                error_type="CalledProcessError",
                message=f"An error occurred while minifying: {e}",
                terminate=True,
            )

    def deploy(self):
        ...

    def test(self):
        ...

    def serve(self):
        dist, static = self.build()
        self.server.run()


# registering classes
bot_factory = BotFactory()
bot_factory.register_bot(BotTypes.BabyQuill.value, BabyQuill)

llm_factory = LLMFactory()
llm_factory.register_llm(LLMTypes.Gpt3_5Turbo.value, Gpt3_5Turbo)

server_factory = ServerFactory()
server_factory.register_server(
    ServerTypes.StaticWebsiteServer.value, StaticWebsiteServer
)

project_factory = ProjectFactory()
project_factory.register_project(ProjectTypes.StaticWebsite.value, StaticWebsite)


if __name__ == "__main__":
    config = Config.init()
    project = project_factory.create_project(config=config)
    pretty.info(f"Running @babyquill {project.name}...")
    project.serve()
