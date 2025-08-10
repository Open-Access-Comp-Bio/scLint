import os
from functools import lru_cache
import configparser
from pathlib import Path

DEFAULT_PATH = Path(__file__).parent.resolve() / "../../../config.ini"

@lru_cache(maxsize=1)
def load_config(path:os.PathLike | str | None = None) -> configparser.ConfigParser:
    config_path = Path(path) if path else Path(os.getenv("APP_CONFIG", DEFAULT_PATH))
    config = configparser.ConfigParser(allow_no_value=True)
    read_config = config.read(config_path)
    if not read_config:
        raise FileNotFoundError(f"Config not found: {config_path}")
    return config

def get_config(section: str) -> dict[str, str]:
    config = load_config()
    return dict(config.items(section))