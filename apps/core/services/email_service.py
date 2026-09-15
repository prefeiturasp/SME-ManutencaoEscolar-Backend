"""
Serviço responsável pelo agendamento do envio de e-mails.

Este módulo fornece uma interface para solicitar o envio assíncrono de e-mails
por meio da task :func:`enviar_email_task`.

A renderização do template e o envio efetivo da mensagem são realizados pela
task do Celery, permitindo que a aplicação não precise aguardar a conclusão do
envio durante a execução da requisição.
"""

from apps.core.tasks import enviar_email_task


class EmailService:
    """
    Centraliza as solicitações de envio assíncrono de e-mails.

    O serviço delega o processamento do e-mail para uma task do Celery.
    Dessa forma, a chamada ao método :meth:`enviar` apenas agenda a tarefa e
    não aguarda a conclusão do envio.

    O e-mail pode ser enviado utilizando um template HTML, dados de contexto,
    uma lista de destinatários e, opcionalmente, anexos.
    """

    @staticmethod
    def enviar(
        assunto: str,
        template: str,
        contexto: dict,
        destinatarios: list[str],
        anexos: list[dict] | None = None,
    ) -> None:
        """Agenda o envio assíncrono de um e-mail HTML.

        Encaminha os dados do e-mail para :func:`enviar_email_task`,
        que é responsável por renderizar o template e realizar o envio da
        mensagem.

        Quando nenhum anexo é informado, ``anexos`` é normalizado para uma
        lista vazia antes que a task seja agendada.

        Args:
            assunto (str): Assunto do e-mail.
            template (str): Caminho do template HTML utilizado para renderizar
                o conteúdo do e-mail..
            contexto (dict): Dados utilizados na renderização do template.
            destinatarios (list[str]): Lista de endereços de e-mail que
                receberão a mensagem.
            anexos (list[dict] | None, optional) :Lista opcional de anexos.
                Cada anexo deve possuir as chaves ``nome``, ``conteudo`` e
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
