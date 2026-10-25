# MindMap Automation Intelligence

MindMap is a simple, clean, and practical Local Python Automation & Job Scheduling Web Application. It allows you to configure existing Python scripts, schedule them (one-time, daily, weekly, or at regular intervals), execute them automatically, and monitor their execution logs directly through a web interface.

Built specifically for local usage on a Windows machine, the application does not rely on heavy external brokers like Celery or Redis. Instead, it utilizes `APScheduler` for background scheduling and standard Python `subprocess` execution to keep things simple, practical, and highly portable.

## Features

- **Automate**: Run your local Python scripts effortlessly via a beautiful web UI.
- **Schedule**: Schedule scripts as one-time, interval-based (e.g., every 5 minutes), daily, or weekly tasks.
- **Execute**: Run jobs asynchronously on demand with a click of a button.
- **Monitor**: Capture standard output (stdout), standard error (stderr), and return codes from scripts.
- **Secure Authentication**: Built-in simple authentication to prevent unauthorized execution of your scripts.

## Technology Stack

- **Backend**: Python 3.x, Flask, SQLite, SQLAlchemy
- **Scheduling**: APScheduler
- **Execution Engine**: Asynchronous execution via `subprocess` and `threading`
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, Bootstrap Icons

---

## 🛠 Installation & Setup

1. **Clone or Download the Repository**
   Ensure you have your files in a folder on your local Windows machine.

2. **Create a Virtual Environment**
   Open PowerShell or Command Prompt in the project folder and run:
   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment**
   ```bash
   .\.venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create an Admin User**
   For security, there is no public registration form. You must create the initial account from the command line:
   ```bash
   python create_user.py admin@example.com my_secure_password
   ```

6. **Run the Application**
   Start the local Flask development server:
   ```bash
   python app.py
   ```

7. **Access the UI**
   Open your browser and navigate to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🚀 Usage Guide

### Creating a Job
1. Log in to the application and navigate to the **Jobs** tab.
2. Click **Create Job**.
3. Provide a name and optional description.
4. Provide the **Script Path**. This must be an absolute path (e.g., `C:\Scripts\data_backup.py`) or relative to the directory where `app.py` is running (e.g., `scripts/test_script.py`).
5. (Optional) Provide command-line arguments separated by spaces.
6. Select a **Schedule Type**:
   - `None`: Manual execution only.
   - `One Time`: Runs once at a specific date and time.
   - `Interval`: Runs repeatedly every N minutes.
   - `Daily`: Runs every day at a specified time.
   - `Weekly`: Runs every week on a specific day and time.
7. Click **Save Job**.

### Running a Job Manually
1. View a job in the **Jobs** tab.
2. Click the **Run Now** button on the right side of the header. 
3. You will be taken to the execution details page where you can monitor the status live.

### Reviewing Logs
1. Navigate to the **Executions** tab to see a history of all automated and manual runs.
2. Click **View Details** on any execution to see the exact CLI command that was run, the final status, execution time, and raw log output.

---

## 🏗 Architecture Details

- **Database**: `instance/mindmap.db` holds the `Job`, `Execution`, and `User` tables.
- **Job Engine**: Found in `executor/executor.py`, handles creating background daemon threads to invoke `subprocess.run()`, capturing output without blocking the main Flask server.
- **Scheduler**: Found in `scheduler/job_manager.py` and `scheduler_config.py`. Uses `BackgroundScheduler` from `APScheduler`. Syncs closely with the database to auto-recover schedules when the server is restarted.

## Disclaimer
This tool is intended for local execution by a trusted user. Since it allows arbitrary execution of local Python scripts via subprocesses, it should **not** be deployed to a public server without additional sandboxing and security hardening.
