"""Task do app core."""

from smtplib import SMTPException
from time import sleep

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = get_task_logger(__name__)


@shared_task
def helchek() -> None:
    """Task de teste do Celery."""
    logger.info("Executando tarefa...")
    sleep(60)
    logger.info("Tarefa finalizada!")


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def enviar_email_task(
    assunto: str,
    template: str,
    contexto: dict,
    destinatarios: list[str],
    anexos: list[dict] | None = None,
) -> None:
    """_summary_.

    Args:
        assunto (str): _description_
        template (str): _description_
        contexto (dict): _description_
        destinatarios (list[str]): _description_
        anexos (list[dict] | None, optional): _description_. Defaults to None.
    """
    html = render_to_string(
        template,
        contexto,
    )

    email = EmailMultiAlternatives(
        subject=assunto,
        body="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=destinatarios,
    )

    email.attach_alternative(html, "text/html")

    for anexo in anexos or []:
        email.attach(
            filename=anexo["nome"],
            content=anexo["conteudo"],
            mimetype=anexo["tipo_conteudo"],
        )

    try:
        email.send()
    except SMTPException:
        logger.exception(
            "Erro ao enviar e-mail de recuperação de senha",
        )
