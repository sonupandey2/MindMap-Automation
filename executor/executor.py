"""
Script executor — runs Python scripts via subprocess.

Provides two entry points:
  execute_job()    — synchronous, used by APScheduler (Phase 5)
  run_job_async()  — starts execution in a background thread, used by Run Now
"""

import os
import sys
import shlex
import subprocess
import threading
from datetime import datetime, timezone

from models import db


def execute_job(job_id, app, execution_id=None):
    """
    Run a job's Python script in a subprocess.

    If execution_id is given, updates that record; otherwise creates one.
    This function is blocking — call it from a thread or APScheduler.
    """
    with app.app_context():
        from models.job import Job           # noqa: F401  — deferred to avoid circular import
        from models.execution import Execution  # noqa: F401

        job = db.session.get(Job, job_id)
        if not job:
            app.logger.error('execute_job: Job %d not found', job_id)
            return None

        # Use an existing execution record or create a new one
        if execution_id:
            execution = db.session.get(Execution, execution_id)
            if not execution:
                app.logger.error(
                    'execute_job: Execution %d not found', execution_id
                )
                return None
        else:
            execution = Execution(job_id=job.id, status='RUNNING')
            db.session.add(execution)
            db.session.commit()

        app.logger.info(
            'Executing job: %s (job_id=%d, execution_id=%d)',
            job.name, job.id, execution.id,
        )

        try:
            # Resolve script path (fallback if absolute path belongs to a moved/renamed directory)
            script_path = job.script_path
            if not os.path.exists(script_path):
                basename = os.path.basename(script_path)
                candidate_in_scripts = os.path.join(app.root_path, 'scripts', basename)
                candidate_in_root = os.path.join(app.root_path, basename)
                if os.path.exists(candidate_in_scripts):
                    script_path = candidate_in_scripts
                elif os.path.exists(candidate_in_root):
                    script_path = candidate_in_root

            # Build the command: python <script> [args...]
            command = [sys.executable, script_path]
            if job.arguments:
                command.extend(shlex.split(job.arguments))

            # Run the script
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=app.config.get('SCRIPT_TIMEOUT', 300),
            )

            execution.completed_at = datetime.now(timezone.utc)
            
            started = execution.started_at
            if started and started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            
            execution.duration = (execution.completed_at - started).total_seconds()
            execution.stdout = result.stdout
            execution.stderr = result.stderr
            execution.return_code = result.returncode
            execution.status = 'SUCCESS' if result.returncode == 0 else 'FAILED'

            if result.returncode == 0:
                app.logger.info('Job succeeded: %s (execution_id=%d)', job.name, execution.id)
            else:
                app.logger.warning(
                    'Job failed: %s (execution_id=%d, returncode=%d)',
                    job.name, execution.id, result.returncode,
                )

        except subprocess.TimeoutExpired as e:
            execution.completed_at = datetime.now(timezone.utc)
            started = execution.started_at
            if started and started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            execution.duration = (execution.completed_at - started).total_seconds()
            execution.status = 'FAILED'
            execution.stdout = e.stdout or ''
            execution.stderr = e.stderr or ''
            execution.error_message = (
                f'Script timed out after {app.config.get("SCRIPT_TIMEOUT", 300)} seconds.'
            )
            app.logger.error('Job timed out: %s (execution_id=%d)', job.name, execution.id)

        except FileNotFoundError:
            execution.completed_at = datetime.now(timezone.utc)
            execution.duration = 0.0
            execution.status = 'FAILED'
            execution.error_message = f'Script not found: {job.script_path}'
            app.logger.error('Script not found: %s', job.script_path)

        except PermissionError:
            execution.completed_at = datetime.now(timezone.utc)
            execution.duration = 0.0
            execution.status = 'FAILED'
            execution.error_message = f'Permission denied: {job.script_path}'
            app.logger.error('Permission denied: %s', job.script_path)

        except Exception as e:
            execution.completed_at = datetime.now(timezone.utc)
            started = execution.started_at
            if started and started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            execution.duration = (execution.completed_at - started).total_seconds()
            execution.status = 'FAILED'
            execution.error_message = str(e)
            app.logger.exception('Unexpected error executing job %s: %s', job.name, e)

        finally:
            try:
                job.last_run_at = datetime.now(timezone.utc)
                db.session.commit()
            except Exception as fe:
                app.logger.error('Error during final DB commit in execute_job: %s', fe)
                
        return execution.id


def run_job_async(job_id, app):
    """
    Create an execution record and start the job in a background thread.

    Returns the execution_id immediately so the caller can redirect to it.
    """
    with app.app_context():
        from models.job import Job           # noqa: F401  — deferred to avoid circular import
        from models.execution import Execution  # noqa: F401

        job = db.session.get(Job, job_id)
        if not job:
            return None

        execution = Execution(job_id=job.id, status='RUNNING')
        db.session.add(execution)
        db.session.commit()
        execution_id = execution.id

    thread = threading.Thread(
        target=execute_job,
        args=(job_id, app, execution_id),
        daemon=True,
    )
    thread.start()
    return execution_id
