"""
Input validation helpers.
"""

import os


def validate_script_path(path):
    """Validate that the script path points to an existing .py file."""
    if not path:
        return 'Python script path is required.'
    if not path.strip().endswith('.py'):
        return 'Script must be a .py file.'
    if not os.path.isfile(path.strip()):
        return f'Script not found: {path}'
    return None


def validate_schedule(schedule_type, schedule_value):
    """Validate schedule type and its associated values."""
    valid_types = ['one_time', 'daily', 'weekly', 'interval']
    if schedule_type not in valid_types:
        return 'Invalid schedule type. Choose One Time, Daily, Weekly, or Interval.'

    if schedule_type == 'one_time':
        if not schedule_value.get('date') or not schedule_value.get('time'):
            return 'Date and time are required for a one-time schedule.'

    elif schedule_type == 'daily':
        if not schedule_value.get('time'):
            return 'Time is required for a daily schedule.'

    elif schedule_type == 'weekly':
        if not schedule_value.get('day') or not schedule_value.get('time'):
            return 'Day and time are required for a weekly schedule.'

    elif schedule_type == 'interval':
        try:
            hours = int(schedule_value.get('hours', 0))
            minutes = int(schedule_value.get('minutes', 0))
        except (TypeError, ValueError):
            return 'Interval hours and minutes must be numbers.'
        if hours <= 0 and minutes <= 0:
            return 'Interval must be at least 1 minute.'

    return None
