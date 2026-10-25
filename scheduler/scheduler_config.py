"""
Scheduler configuration and initialization.
"""

from apscheduler.schedulers.background import BackgroundScheduler
import logging
from executor.executor import execute_job

logger = logging.getLogger('scheduler')

# Global scheduler instance
scheduler = BackgroundScheduler()

def run_job_with_context(app, job_id):
    """
    Wrapper function to execute a job within the Flask application context.
    This is necessary because the job interacts with the database (SQLAlchemy)
    which requires an active app context.
    """
    logger.info(f"Executing scheduled job ID: {job_id}")
    # Note: execute_job opens its own app_context internally,
    # so we do NOT wrap it in another `with app.app_context()` here.
    execute_job(job_id, app)
