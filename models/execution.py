"""
Execution model — represents a single run of a job.
"""

from datetime import datetime, timezone
from models import db


class Execution(db.Model):
    __tablename__ = 'executions'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Float, nullable=True)          # seconds
    status = db.Column(db.String(20), nullable=False, default='RUNNING')  # RUNNING, SUCCESS, FAILED
    return_code = db.Column(db.Integer, nullable=True)
    stdout = db.Column(db.Text, nullable=True)
    stderr = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Execution {self.id} | Job {self.job_id} | {self.status}>'
