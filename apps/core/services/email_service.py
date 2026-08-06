"""_summary_."""

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
        """_summary_.

        Args:
            assunto (str): _description_
            template (str): _description_
            contexto (dict): _description_
            destinatarios (list[str]): _description_
            anexos (list[dict] | None, optional): _description_.
                Defaults to None.
        """
        anexos = anexos or []

        enviar_email_task.delay(
            assunto=assunto,
            template=template,
            contexto=contexto,
            destinatarios=destinatarios,
            anexos=anexos,
        )
