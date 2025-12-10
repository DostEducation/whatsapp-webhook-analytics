"""Flask configuration."""

import os
from os import path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

FLASK_APP = os.environ.get("FLASK_APP", "development")

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "DEBUG")
