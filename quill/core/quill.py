from quill.core.config import Config


class Quill:
    def __init__(self) -> None:
        self.config: Config = None
        self.projects: list = None
        self.init()

    def init(self):
        self.config = Config()
        self.projects = []