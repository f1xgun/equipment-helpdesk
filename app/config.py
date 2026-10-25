import os
from pathlib import Path

from dotenv import dotenv_values

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def get_database_url():
    file_settings = dotenv_values(ENV_FILE)
    default_url = file_settings.get("DATABASE_URL") or "sqlite:///./helpdesk.db"
    return os.getenv("DATABASE_URL", default_url)
