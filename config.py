"""Flask configuration."""

import os

FLASK_APP = os.environ.get("FLASK_APP", "development")

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", None)

if FLASK_APP == "development":
    # Fetch env from the .env file
    from dotenv import load_dotenv

    load_dotenv()

    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "DEBUG")
