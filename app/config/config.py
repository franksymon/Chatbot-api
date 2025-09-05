import abc
import os


class Singleton(abc.ABCMeta, type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):

    """
    Config class for managing environment variables.
    """

    def __init__(self) -> None:
        super().__init__()

        self.langchain_tracing = os.getenv("LANGCHAIN_TRACING")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))

        # OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        # Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        

config = Config()