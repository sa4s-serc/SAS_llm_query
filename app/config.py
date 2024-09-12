import os
from typing import Optional

APP_NAME: str = "IIIT Companion"
BUILDER_PORT: int = 8501
MIN_PORT: int = 9000
MAX_PORT: int = 9999

# These paths will be set dynamically when the config is loaded
APP_DIR: Optional[str] = None
MICROSERVICES_DIR: Optional[str] = None
GENERATED_APPS_DIR: Optional[str] = None


def set_paths(base_path: str) -> None:
    global APP_DIR, MICROSERVICES_DIR, GENERATED_APPS_DIR
    APP_DIR = base_path
    MICROSERVICES_DIR = os.path.join(base_path, "microservices")
    GENERATED_APPS_DIR = os.path.join(base_path, "generated_apps")


def setup():
    if APP_DIR is None or MICROSERVICES_DIR is None or GENERATED_APPS_DIR is None:
        raise ValueError("Paths are not set. Call set_paths() first.")
    os.makedirs(GENERATED_APPS_DIR, exist_ok=True)
