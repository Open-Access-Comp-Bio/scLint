import os
from functools import lru_cache
import configparser
from pathlib import Path

DEFAULT_PATH = Path(__file__).parent.resolve() / "../../../config.ini"


@lru_cache(maxsize=1)
def load_config(path: os.PathLike | str | None = None) -> configparser.ConfigParser:
    config_path = Path(path) if path else Path(os.getenv("APP_CONFIG", DEFAULT_PATH))
    config = configparser.ConfigParser(allow_no_value=True)
    read_config = config.read(config_path)
    if not read_config:
        raise FileNotFoundError(f"Config not found: {config_path}")
    return config


def get_config(section: str, path: os.PathLike | str | None = None) -> dict[str, str | None]:
    config = load_config(path)
    out: dict[str, str | None] = {}

    for k, v in config.items(section):
        # configparser can return None if allow_no_value=True and it was truly blank
        if v is None:
            out[k] = None
            continue

        v = v.strip().strip('"').strip("'")  # remove accidental quotes

        if v == "" or v.lower() == "none":
            out[k] = None
        else:
            out[k] = v

    return out
