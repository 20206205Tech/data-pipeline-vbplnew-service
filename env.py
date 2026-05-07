import os

from environs import Env
from loguru import logger

env = Env()
logger.info("Loading environment variables...")


ENVIRONMENT = env.str("ENVIRONMENT", "production")
RELOAD = True if ENVIRONMENT == "development" else False


SERVICE_NAME = "data-pipeline-vbplnew-service"
PORT = env.int("SERVICE_PORT", 51002)


DATA_PIPELINE_VBPLNEW_DATABASE_URL = env.str("DATA_PIPELINE_VBPLNEW_DATABASE_URL")
DATABASE_URL = DATA_PIPELINE_VBPLNEW_DATABASE_URL


SUPABASE_PROJECT_ID = env.str("SUPABASE_PROJECT_ID")
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
ISSUER = f"{SUPABASE_URL}/auth/v1"
AUDIENCE = "authenticated"


DESCRIPTION = f"""
# Chào mừng đến với {SERVICE_NAME} ({ENVIRONMENT})

* [Google](https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1/authorize?provider=google)
* [Database](https://console.neon.tech/app/org-still-feather-82034197/projects?q={SERVICE_NAME})
* [Local](http://localhost:{PORT})
* [Dev](https://dev-{SERVICE_NAME}.20206205.tech)

""".strip()


logger.success(f"DESCRIPTION: \n{DESCRIPTION}")


PATH_FILE_ENV = os.path.abspath(__file__)
PATH_FOLDER_PROJECT = os.path.dirname(PATH_FILE_ENV)
PATH_FOLDER_DATA = os.path.join(PATH_FOLDER_PROJECT, "data")
PATH_FOLDER_DOCS = os.path.join(PATH_FOLDER_PROJECT, "docs")


if not os.path.exists(PATH_FOLDER_DATA):
    os.makedirs(PATH_FOLDER_DATA)

if not os.path.exists(PATH_FOLDER_DOCS):
    os.makedirs(PATH_FOLDER_DOCS)
