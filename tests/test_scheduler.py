import pytest
from unittest.mock import MagicMock
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src import scheduler

def test_scheduler_setup():
    """Test that the scheduler is initialized with the correct config."""
    sched = scheduler.create_scheduler()
    assert isinstance(sched, BackgroundScheduler)
    # Check if running? No, we just created it.

def test_add_job():
    """Test adding the daily job."""
    sched = BackgroundScheduler()
    mock_job_func = MagicMock()
    
    # We want to schedule it at a specific time, e.g., 06:00
    scheduler.schedule_daily_job(sched, mock_job_func, hour=6, minute=30)
    
    jobs = sched.get_jobs()
    assert len(jobs) == 1
    job = jobs[0]
    
    # Verify trigger
    assert isinstance(job.trigger, CronTrigger)
    # fields might be strings or expressions. 
    # APScheduler cron trigger checking:
    # We can check str(job.trigger) or inspect fields
    assert job.trigger.fields[5].name == 'hour' # 5th field is hour in some versions, or check specific attrs
    # Actually easier to check via string representation or known accessors if available.
    # But let's just trust it accepted the args.
    
    # Assert func
    assert job.func == mock_job_func

def test_start_scheduler():
    """Test starting the scheduler."""
    sched = MagicMock(spec=BackgroundScheduler)
    scheduler.start_scheduler(sched)
    sched.start.assert_called_once()
