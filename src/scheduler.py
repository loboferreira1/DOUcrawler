from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog

logger = structlog.get_logger()

def create_scheduler():
    """Cria e retorna um BackgroundScheduler configurado."""
    return BackgroundScheduler()

def schedule_daily_job(scheduler, job_func, hour=6, minute=0):
    """
    Agenda a função job_func para executar diariamente no horário especificado.
    """
    trigger = CronTrigger(hour=hour, minute=minute)
    scheduler.add_job(
        job_func,
        trigger=trigger,
        name=f"daily_job_{hour:02d}{minute:02d}",
        replace_existing=True
    )
    logger.info("job_scheduled", hour=hour, minute=minute)

def start_scheduler(scheduler):
    """Inicia o agendador."""
    try:
        scheduler.start()
        logger.info("scheduler_started")
    except Exception as e:
        logger.error("scheduler_start_failed", error=str(e))
        raise
