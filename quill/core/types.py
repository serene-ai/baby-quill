from aenum import Enum, extend_enum
from abc import ABC

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ExtendableEnum(str, Enum):
    @classmethod
    def extend(cls, name, *args, **kwargs):
        extend_enum(cls, name, *args, **kwargs)
    
    @classmethod
    def get_options(cls):
        return [option.value for option in cls]

    @classmethod
    def default(cls):
        return cls.get_options()[0] if cls.get_options() else None


class LLMTypes(ExtendableEnum):...

class BotTypes(ExtendableEnum):...

class ProjectTypes(ExtendableEnum):...

class ServerTypes(ExtendableEnum):...
