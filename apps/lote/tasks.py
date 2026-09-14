"""Tasks do domínio de lotes."""

from celery import shared_task
from django.core.management import call_command


@shared_task
def executar_validade_lote() -> None:
    """Executa o comando que inativa os lotes expirados."""
    call_command("inativar_lotes_expirados")
