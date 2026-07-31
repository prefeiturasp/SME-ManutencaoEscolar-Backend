"""Task do app core."""

from time import sleep

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def helchek() -> None:
    """Task de teste do Celery."""
    logger.info("Executando tarefa...")
    sleep(60)
    logger.info("Tarefa finalizada!")
