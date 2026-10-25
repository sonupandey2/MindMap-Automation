"""
Jobs routes — create, list, view, edit, delete jobs.
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from models import db
from models.job import Job
from models.execution import Execution
from utils.validators import validate_script_path, validate_schedule
from executor.executor import run_job_async
from scheduler.job_manager import schedule_job, remove_job

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs_bp.before_request
@login_required
def require_login():
    pass


# ── Helper ────────────────────────────────────────────────
def _build_schedule_value(form):
    """Extract schedule fields from the submitted form."""
    schedule_type = form.get('schedule_type', '').strip()
    schedule_value = {}

    if schedule_type == 'one_time':
        schedule_value = {
            'date': form.get('schedule_date', '').strip(),
            'time': form.get('schedule_time', '').strip(),
        }
    elif schedule_type == 'daily':
        schedule_value = {
            'time': form.get('schedule_time', '').strip(),
        }
    elif schedule_type == 'weekly':
        schedule_value = {
            'day': form.get('schedule_day', '').strip(),
            'time': form.get('schedule_time', '').strip(),
        }
    elif schedule_type == 'interval':
        schedule_value = {
            'hours': form.get('interval_hours', '0').strip(),
            'minutes': form.get('interval_minutes', '0').strip(),
        }

    return schedule_type, schedule_value


def _validate_job_form(name, script_path, schedule_type, schedule_value):
    """Run all validations and return a list of error messages."""
    errors = []
    if not name:
        errors.append('Job name is required.')

    path_error = validate_script_path(script_path)
    if path_error:
        errors.append(path_error)

    schedule_error = validate_schedule(schedule_type, schedule_value)
    if schedule_error:
        errors.append(schedule_error)

    return errors


PER_PAGE = 10

# ── List Jobs ─────────────────────────────────────────────
@jobs_bp.route('/')
def list_jobs():
    """Display all jobs with pagination."""
    page        = request.args.get('page', 1, type=int)
    total       = Job.query.count()
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page        = max(1, min(page, total_pages))
    jobs        = Job.query.order_by(Job.created_at.desc()).offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()
    return render_template('jobs.html', jobs=jobs, page=page, total_pages=total_pages, total=total, per_page=PER_PAGE)


# ── Create Job ────────────────────────────────────────────
@jobs_bp.route('/create', methods=['GET', 'POST'])
def create_job():
    """Show the create-job form or process submission."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        script_path = request.form.get('script_path', '').strip()
        arguments = request.form.get('arguments', '').strip()
        schedule_type, schedule_value = _build_schedule_value(request.form)

        errors = _validate_job_form(name, script_path, schedule_type, schedule_value)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'create_job.html',
                name=name, description=description,
                script_path=script_path, arguments=arguments,
                schedule_type=schedule_type, schedule_value=schedule_value,
            )

        job = Job(
            name=name,
            description=description,
            script_path=script_path,
            arguments=arguments,
            schedule_type=schedule_type,
            schedule_value=json.dumps(schedule_value),
            status='ACTIVE',
        )
        db.session.add(job)
        db.session.commit()
        
        # Add job to scheduler
        schedule_job(job, current_app._get_current_object())

        current_app.logger.info('Job created: %s (id=%d)', job.name, job.id)
        flash('Job created successfully.', 'success')
        return redirect(url_for('jobs.view_job', job_id=job.id))

    return render_template('create_job.html')


# ── View Job ──────────────────────────────────────────────
@jobs_bp.route('/<int:job_id>')
def view_job(job_id):
    """Display job details and recent executions."""
    job = db.get_or_404(Job, job_id)
    schedule_value = json.loads(job.schedule_value) if job.schedule_value else {}

    recent_executions = (
        Execution.query
        .filter_by(job_id=job.id)
        .order_by(Execution.started_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        'job_details.html',
        job=job,
        schedule_value=schedule_value,
        recent_executions=recent_executions,
    )


# ── Edit Job ──────────────────────────────────────────────
@jobs_bp.route('/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    """Show the edit form or process update."""
    job = db.get_or_404(Job, job_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        script_path = request.form.get('script_path', '').strip()
        arguments = request.form.get('arguments', '').strip()
        schedule_type, schedule_value = _build_schedule_value(request.form)

        errors = _validate_job_form(name, script_path, schedule_type, schedule_value)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'edit_job.html', job=job,
                name=name, description=description,
                script_path=script_path, arguments=arguments,
                schedule_type=schedule_type, schedule_value=schedule_value,
            )

        job.name = name
        job.description = description
        job.script_path = script_path
        job.arguments = arguments
        job.schedule_type = schedule_type
        job.schedule_value = json.dumps(schedule_value)
        db.session.commit()
        
        # Update scheduler (schedule_job handles invalid/missing triggers gracefully)
        schedule_job(job, current_app._get_current_object())

        current_app.logger.info('Job updated: %s (id=%d)', job.name, job.id)
        flash('Job updated successfully.', 'success')
        return redirect(url_for('jobs.view_job', job_id=job.id))

    schedule_value = json.loads(job.schedule_value) if job.schedule_value else {}
    return render_template('edit_job.html', job=job, schedule_value=schedule_value)


# ── Delete Job ────────────────────────────────────────────
@jobs_bp.route('/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    """Delete a job and all its executions."""
    job = db.get_or_404(Job, job_id)
    job_name = job.name
    db.session.delete(job)
    db.session.commit()
    
    # Remove from scheduler
    remove_job(job_id)

    current_app.logger.info('Job deleted: %s (id=%d)', job_name, job_id)
    flash('Job deleted successfully.', 'success')
    return redirect(url_for('jobs.list_jobs'))


# ── Run Now ───────────────────────────────────────────────
@jobs_bp.route('/<int:job_id>/run', methods=['POST'])
def run_now(job_id):
    """Execute a job immediately in a background thread."""
    job = db.get_or_404(Job, job_id)
    execution_id = run_job_async(job.id, current_app._get_current_object())

    if execution_id:
        current_app.logger.info('Run Now: %s (execution=%d)', job.name, execution_id)
        flash('Job started successfully.', 'success')
        return redirect(url_for('executions.view_execution', execution_id=execution_id))

    flash('Failed to start job.', 'danger')
    return redirect(url_for('jobs.view_job', job_id=job_id))
