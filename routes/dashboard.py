"""
Dashboard route — summary cards, recent executions, upcoming jobs.
"""

from flask import Blueprint, render_template
from flask_login import login_required
from models import db
from models.job import Job
from models.execution import Execution

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.before_request
@login_required
def require_login():
    pass


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    """Render the main dashboard page."""

    # Summary counts
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(status='ACTIVE').count()
    successful_executions = Execution.query.filter_by(status='SUCCESS').count()
    failed_executions = Execution.query.filter_by(status='FAILED').count()
    running_executions = Execution.query.filter_by(status='RUNNING').count()

    # Last 10 executions (with job name via join)
    recent_executions = (
        db.session.query(Execution, Job.name)
        .join(Job)
        .order_by(Execution.started_at.desc())
        .limit(10)
        .all()
    )

    # Active jobs that have a scheduled next run
    upcoming_jobs = (
        Job.query
        .filter_by(status='ACTIVE')
        .filter(Job.next_run_at.isnot(None))
        .order_by(Job.next_run_at.asc())
        .limit(10)
        .all()
    )

    return render_template(
        'dashboard.html',
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        successful_executions=successful_executions,
        failed_executions=failed_executions,
        running_executions=running_executions,
        recent_executions=recent_executions,
        upcoming_jobs=upcoming_jobs,
    )
