import os
from pathlib import Path


class Settings:
    APP_NAME: str = "GugaGit"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Nível de Log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Timeout padrão para comandos de terminal (segundos)
    COMMAND_TIMEOUT: int = 30

settings = Settings()