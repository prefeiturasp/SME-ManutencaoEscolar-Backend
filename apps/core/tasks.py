"""Tasks assíncronas utilizadas pela aplicação Core.

Define tarefas executadas pelo Celery, incluindo uma tarefa de verificação
e o envio assíncrono de e-mails HTML.
"""

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
    """Executa uma tarefa de teste para verificar o funcionamento do Celery.

    Registra o início da execução, aguarda 60 segundos e registra a conclusão
    da tarefa.
    """
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
    """Renderiza e envia um e-mail HTML de forma assíncrona.

    Renderiza o template informado utilizando o contexto recebido, cria
    uma mensagem HTML, adiciona os anexos informados e realiza o envio
    utilizando as configurações de e-mail da aplicação.

    A task está configurada para realizar novas tentativas automaticamente
    em caso de exceções, utilizando backoff progressivo e um limite de
    cinco tentativas.

    Args:
        assunto (str): Assunto do e-mail.
        template (str): Caminho do template HTML.
        contexto (dict): Dados utilizados na renderização do template.
        destinatarios (list[str]): Lista de destinatários.
        anexos (list[dict] | None, optional): Lista de anexos. Cada
            anexo deve possuir as chaves ``nome``, ``conteudo`` e
            ``tipo_conteudo``. Defaults to ``None``.
    Returns:
        None: A task não retorna dados após o envio.

    Raises:
        Exception: Exceções ocorridas durante a execução podem provocar
            uma nova tentativa automática pelo Celery, conforme a política
            configurada para a task.
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
