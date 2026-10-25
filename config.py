"""
Application configuration.
"""

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Central configuration for the Flask application."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # SQLite database stored in the instance/ directory
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'automation.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Maximum time (in seconds) a script is allowed to run before being killed
    SCRIPT_TIMEOUT = 300
