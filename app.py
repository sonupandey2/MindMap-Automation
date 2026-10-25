"""
Python Automation & Job Scheduling Web Application

Entry point — run this file to start the Flask server:
    python app.py
"""

import os
import json
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db
from utils.logger import setup_logger


def create_app():
    """Application factory — creates and configures the Flask app."""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure the instance directory exists (SQLite database lives here)
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    # ── Database ──────────────────────────────────────────────
    db.init_app(app)

    with app.app_context():
        # Import models so SQLAlchemy registers them before create_all()
        from models.job import Job           # noqa: F401
        from models.execution import Execution  # noqa: F401
        from models.user import User         # noqa: F401
        db.create_all()

    # ── Logging ───────────────────────────────────────────────
    setup_logger(app)
    app.logger.info('Database initialized — tables created')

    # ── Authentication ────────────────────────────────────────
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return db.session.get(User, int(user_id))

    # ── Blueprints ────────────────────────────────────────────
    from routes.dashboard import dashboard_bp
    from routes.jobs import jobs_bp
    from routes.executions import executions_bp
    from routes.auth import auth_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(executions_bp)
    app.register_blueprint(auth_bp)

    # ── Job Scheduling (APScheduler) ──────────────────────────
    from scheduler.scheduler_config import scheduler
    from scheduler.job_manager import load_all_jobs
    
    # Start the scheduler if it's not already running
    if not scheduler.running:
        scheduler.start()
        app.logger.info("APScheduler started")
        
        # Load all scheduled jobs from the database
        load_all_jobs(app)

    # ── Template Filters ──────────────────────────────────────
    @app.template_filter('format_schedule')
    def format_schedule(job):
        """Return a human-readable schedule description."""
        try:
            sv = json.loads(job.schedule_value)
        except (json.JSONDecodeError, TypeError):
            return job.schedule_type.replace('_', ' ').title()

        day_names = {
            'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday',
            'thu': 'Thursday', 'fri': 'Friday', 'sat': 'Saturday', 'sun': 'Sunday',
        }

        if job.schedule_type == 'one_time':
            return f"Once on {sv.get('date', '?')} at {sv.get('time', '?')}"
        elif job.schedule_type == 'daily':
            return f"Daily at {sv.get('time', '?')}"
        elif job.schedule_type == 'weekly':
            day = day_names.get(sv.get('day', ''), sv.get('day', '?'))
            return f"Every {day} at {sv.get('time', '?')}"
        elif job.schedule_type == 'interval':
            h, m = int(sv.get('hours', 0)), int(sv.get('minutes', 0))
            parts = []
            if h: parts.append(f"{h}h")
            if m: parts.append(f"{m}m")
            return f"Every {' '.join(parts)}" if parts else 'Interval'
        return job.schedule_type.replace('_', ' ').title()

    # ── Error Handlers ────────────────────────────────────────
    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    # ── Health check ──────────────────────────────────────────
    @app.route('/health')
    def health():
        return {
            'status': 'ok',
            'message': 'MindMap is running',
        }

    return app


# ── Run the application ──────────────────────────────────────
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
