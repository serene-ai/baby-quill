from typing import Optional

from openai import ChatCompletion

from quill.bot import BaseBot, BotFactory
from quill.core.config import Config
from quill.core.types import BotTypes, LLMTypes, ProjectTypes, ServerTypes
from quill.llm import BaseLLM, LLMFactory
from quill.project import BaseProject, ProjectFactory
from quill.server import BaseServer, ServerFactory

from quill.core.pretty import Pretty

BotTypes.extend("BabyQuill", "baby-quill")
LLMTypes.extend("Gpt3_5Turbo", "gpt-3.5-turbo")
ProjectTypes.extend("StaticWebsite", "static-website")
ServerTypes.extend("StaticWebsiteServer", "static-website-server")

pretty = Pretty()

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

    def init(self):
        self.name = ServerTypes.StaticWebsiteServer.value

    def run(self, port: Optional[int] = 4455):
        pretty.message(f"Running {self.name} at http://localhost:{port}")


class StaticWebsite(BaseProject):
    """Build static websites with Quill"""

    def init(self, config: Config):
        project_config = config.project
        self.name = project_config.name
        self.project_type = ProjectTypes.StaticWebsite.value
        self.project_root = project_config.project_type

    def build(self):
        ...

    def deploy(self):
        ...

    def test(self):
        ...

    def serve(self):
        self.server.run()


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