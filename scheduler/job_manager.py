"""
Functions to map database Job records to APScheduler jobs.
"""

from scheduler.scheduler_config import scheduler, run_job_with_context
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
import logging
from datetime import datetime
import json

logger = logging.getLogger('job_manager')

def _build_trigger(job):
    """
    Builds the appropriate APScheduler trigger based on the job's schedule_type
    and schedule_value.
    """
    if job.schedule_type == 'one_time':
        # schedule_value is JSON string, e.g., '{"date": "2026-10-01", "time": "15:30"}'
        try:
            config = json.loads(job.schedule_value)
            date_str = config.get('date', '')
            time_str = config.get('time', '')
            run_date = datetime.fromisoformat(f"{date_str}T{time_str}")
            return DateTrigger(run_date=run_date)
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Invalid date format for one_time job {job.id}: {e}")
            return None
            
    elif job.schedule_type == 'interval':
        # schedule_value is JSON string, e.g., '{"hours": "0", "minutes": "2"}'
        try:
            config = json.loads(job.schedule_value)
            hours = int(config.get('hours', 0))
            minutes = int(config.get('minutes', 0))
            if hours == 0 and minutes == 0:
                 return None
            return IntervalTrigger(hours=hours, minutes=minutes)
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Invalid interval value for job {job.id}: {e}")
            return None
            
    elif job.schedule_type == 'daily':
        # schedule_value is JSON string, e.g., '{"time": "14:30"}'
        try:
            config = json.loads(job.schedule_value)
            time_parts = config.get('time', '00:00').split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            return CronTrigger(hour=hour, minute=minute)
        except (ValueError, IndexError, json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Invalid daily time format for job {job.id}: {e}")
            return None
            
    elif job.schedule_type == 'weekly':
        # schedule_value is JSON string, e.g., '{"day": "mon", "time": "09:00"}'
        try:
            config = json.loads(job.schedule_value)
            day = config.get('day')
            time_parts = config.get('time', '00:00').split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            return CronTrigger(day_of_week=day, hour=hour, minute=minute)
        except (ValueError, IndexError, json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Invalid weekly config for job {job.id}: {e}")
            return None

    return None


def schedule_job(job, app):
    """
    Adds or updates a job in the APScheduler instance.
    The job ID in APScheduler is matched to the database Job ID.
    """
    if not job.schedule_type or job.schedule_type == 'none':
        # Job has no automated schedule
        return
        
    trigger = _build_trigger(job)
    if not trigger:
        return

    job_id_str = str(job.id)
    
    # If it already exists, replace it
    if scheduler.get_job(job_id_str):
        scheduler.reschedule_job(job_id_str, trigger=trigger)
        logger.info(f"Rescheduled job {job.id} in APScheduler")
    else:
        scheduler.add_job(
            func=run_job_with_context,
            trigger=trigger,
            args=[app, job.id],
            id=job_id_str,
            replace_existing=True,
            name=job.name
        )
        logger.info(f"Added job {job.id} to APScheduler")


def remove_job(job_id):
    """
    Removes a job from the APScheduler instance if it exists.
    """
    job_id_str = str(job_id)
    if scheduler.get_job(job_id_str):
        scheduler.remove_job(job_id_str)
        logger.info(f"Removed job {job_id} from APScheduler")


def load_all_jobs(app):
    """
    Loads all scheduled jobs from the database into APScheduler.
    Typically called once on application startup.
    """
    with app.app_context():
        from models.job import Job
        jobs = Job.query.filter(
            Job.schedule_type.isnot(None),
            Job.schedule_type != 'none',
            Job.schedule_type != ''
        ).all()
        count = 0
        for job in jobs:
            schedule_job(job, app)
            count += 1
        
        logger.info(f"Loaded {count} jobs into APScheduler from the database")
