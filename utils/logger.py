"""
Application-wide logging setup.

Creates a rotating log file at logs/app.log.
"""

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """Configure file-based logging for the Flask application."""

    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, 'app.log')

    # Rotate at 1 MB, keep 5 backup files
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_024 * 1_024, backupCount=5,
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')
