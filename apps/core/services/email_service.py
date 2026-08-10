"""Serviço para gerenciar envio de e-mail."""

from apps.core.tasks import enviar_email_task


class EmailService:
    """Serviço responsável por solicitar o envio assíncrono de e-mails."""

    @staticmethod
    def enviar(
        assunto: str,
        template: str,
        contexto: dict,
        destinatarios: list[str],
        anexos: list[dict] | None = None,
    ) -> None:
        """Solicite o envio assíncrono de um e-mail HTML.

        Encaminha a solicitação para uma task do Celery responsável
        por renderizar o template e realizar o envio do e-mail.

        Args:
            assunto (str): Assunto do e-mail.
            template (str): Caminho do template HTML.
            contexto (dict): Dados utilizados na renderização do template.
            destinatarios (list[str]): Lista de destinatários.
            anexos (list[dict] | None, optional):Lista de anexos. Cada
                anexo deve possuir as chaves ``nome``, ``conteudo`` e
                ``tipo_conteudo``. Defaults to ``None``.
        """
        anexos = anexos or []

        enviar_email_task.delay(
            assunto=assunto,
            template=template,
            contexto=contexto,
            destinatarios=destinatarios,
            anexos=anexos,
        )
