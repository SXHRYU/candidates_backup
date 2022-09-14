import os
from pathlib import Path


# Auth variables.
USERNAME: str = os.getenv("USERNAME")
PASSWORD: str = os.getenv("PASSWORD")
API_TOKEN: str = os.getenv("API_TOKEN")
ADMIN_ID: int = int(os.getenv("ADMIN_ID"))

# URL variables.
USERS_LIST_URL: str = os.getenv("USERS_LIST_URL")
REGISTER_URL: str = os.getenv("REGISTER_URL")
TASKS_URL: str = os.getenv("TASKS_URL")

# Bot variables.
BOT_TOKEN: str = os.getenv("BOT_TOKEN")

# HR variables.
HR_USERS: tuple[int] = tuple(map(int, os.getenv("HR_USERS").split()))

# Metrics variables.
PLATE_VALUES: tuple[str] = tuple(os.getenv("PLATE_VALUES").split())

# Database tables variales.
# Candidates table name.
CANDIDATES: str = os.getenv("CANDIDATES")
# Metrics table name.
METRICS: str = os.getenv("METRICS")

# Database auth variables.
DB_HOST: str = os.getenv("DB_HOST")
DB_PORT: int = int(os.getenv("DB_PORT"))
DB_NAME: str = os.getenv("DB_NAME")
DB_USER: str = os.getenv("DB_USER")
DB_PASSWORD: str = os.getenv("DB_PASSWORD")

# Directory paths variables.
ROOT_DIR: Path = Path(os.getenv("ROOT_DIR"))
ALL_RESULTS_EXCEL_DIR: Path = Path(os.getenv("ALL_RESULTS_EXCEL_DIR"))
USER_IMAGES_DIR: Path = Path(os.getenv("USER_IMAGES_DIR"))
ORIGINAL_IMAGES_DIR: Path = Path(os.getenv("ORIGINAL_IMAGES_DIR"))
