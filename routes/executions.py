"""
Executions routes — history list, details, and retry.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from models import db
from models.job import Job
from models.execution import Execution
from executor.executor import run_job_async

executions_bp = Blueprint('executions', __name__, url_prefix='/executions')

@executions_bp.before_request
@login_required
def require_login():
    pass


PER_PAGE = 10

@executions_bp.route('/')
def list_executions():
    """Display execution history with optional filtering and pagination."""
    job_id  = request.args.get('job_id', type=int)
    status  = request.args.get('status', '').strip().upper()
    page    = request.args.get('page', 1, type=int)

    query = db.session.query(Execution, Job.name).join(Job)

    if job_id:
        query = query.filter(Execution.job_id == job_id)
    if status in ('RUNNING', 'SUCCESS', 'FAILED'):
        query = query.filter(Execution.status == status)

    query = query.order_by(Execution.started_at.desc())

    total       = query.count()
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page        = max(1, min(page, total_pages))
    executions  = query.offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()

    jobs = Job.query.order_by(Job.name).all()

    return render_template(
        'executions.html',
        executions=executions,
        jobs=jobs,
        filter_job_id=job_id,
        filter_status=status,
        page=page,
        total_pages=total_pages,
        total=total,
        per_page=PER_PAGE,
    )


@executions_bp.route('/<int:execution_id>')
def view_execution(execution_id):
    """Display full details of a single execution."""
    execution = db.get_or_404(Execution, execution_id)
    job = db.session.get(Job, execution.job_id)

    return render_template(
        'execution_details.html',
        execution=execution,
        job=job,
    )


@executions_bp.route('/<int:execution_id>/run', methods=['POST'])
def retry_execution(execution_id):
    """Re-run the job associated with a failed execution."""
    execution = db.get_or_404(Execution, execution_id)
    job = db.session.get(Job, execution.job_id)

    if not job:
        flash('Associated job no longer exists.', 'danger')
        return redirect(url_for('executions.list_executions'))

    new_execution_id = run_job_async(job.id, current_app._get_current_object())

    if new_execution_id:
        current_app.logger.info('Retrying job: %s (new execution=%d)', job.name, new_execution_id)
        flash('Job started successfully.', 'success')
        return redirect(url_for('executions.view_execution', execution_id=new_execution_id))

    flash('Failed to start job.', 'danger')
    return redirect(url_for('executions.view_execution', execution_id=execution_id))
