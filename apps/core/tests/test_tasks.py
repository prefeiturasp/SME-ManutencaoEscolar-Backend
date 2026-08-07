from smtplib import SMTPException
from unittest.mock import MagicMock, patch

from apps.core.tasks import enviar_email_task, helchek


class TestHelchek:
    @patch("apps.core.tasks.sleep")
    @patch("apps.core.tasks.logger")
    def test_helchek_loga_inicio_e_fim_e_aguarda_60_segundos(
        self, mock_logger, mock_sleep
    ):
        helchek()

        mock_sleep.assert_called_once_with(60)
        mock_logger.info.assert_any_call("Executando tarefa...")
        mock_logger.info.assert_any_call("Tarefa finalizada!")
        assert mock_logger.info.call_count == 2


class TestEnviarEmailTask:
    @patch("apps.core.tasks.render_to_string")
    @patch("apps.core.tasks.EmailMultiAlternatives")
    def test_deve_enviar_email_html(
        self,
        email_mock,
        render_mock,
    ):
        render_mock.return_value = "<html></html>"

        email = MagicMock()
        email_mock.return_value = email

        enviar_email_task(
            assunto="Teste",
            template="emails/teste.html",
            contexto={"nome": "João"},
            destinatarios=["teste@email.com"],
        )

        render_mock.assert_called_once_with(
            "emails/teste.html",
            {"nome": "João"},
        )

        email.attach_alternative.assert_called_once_with(
            "<html></html>",
            "text/html",
        )

        email.send.assert_called_once()

    @patch("apps.core.tasks.render_to_string")
    @patch("apps.core.tasks.EmailMultiAlternatives")
    def test_deve_anexar_arquivo(
        self,
        email_mock,
        render_mock,
    ):
        email = MagicMock()
        email_mock.return_value = email

        enviar_email_task(
            assunto="Teste",
            template="emails/teste.html",
            contexto={},
            destinatarios=["teste@email.com"],
            anexos=[
                {
                    "nome": "arquivo.pdf",
                    "conteudo": b"abc",
                    "tipo_conteudo": "application/pdf",
                }
            ],
        )

        email.attach.assert_called_once_with(
            filename="arquivo.pdf",
            content=b"abc",
            mimetype="application/pdf",
        )

    @patch("apps.core.tasks.logger")
    @patch("apps.core.tasks.EmailMultiAlternatives")
    @patch("apps.core.tasks.render_to_string")
    def test_deve_registrar_erro_no_envio(
        self,
        render_mock,
        email_mock,
        logger_mock,
    ):
        email = MagicMock()
        email.send.side_effect = SMTPException()

        email_mock.return_value = email

        enviar_email_task(
            assunto="Teste",
            template="emails/teste.html",
            contexto={},
            destinatarios=["teste@email.com"],
        )

        logger_mock.exception.assert_called_once()
