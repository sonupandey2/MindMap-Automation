"""
Job model — represents a configured automation job.
"""

from datetime import datetime, timezone
from models import db


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    script_path = db.Column(db.String(500), nullable=False)
    arguments = db.Column(db.String(500), nullable=True, default='')
    schedule_type = db.Column(db.String(20), nullable=False)       # one_time, daily, weekly, interval
    schedule_value = db.Column(db.Text, nullable=False)            # JSON string with schedule config
    status = db.Column(db.String(20), nullable=False, default='ACTIVE')  # ACTIVE
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_run_at = db.Column(db.DateTime, nullable=True)
    next_run_at = db.Column(db.DateTime, nullable=True)

    # One Job → Many Executions
    executions = db.relationship(
        'Execution', backref='job', lazy=True, cascade='all, delete-orphan',
    )

    def __repr__(self):
        return f'<Job {self.id}: {self.name}>'
