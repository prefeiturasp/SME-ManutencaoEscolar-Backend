from unittest.mock import patch

from apps.core.services.email_service import EmailService


class TestEmailService:
    """Testes do serviço de e-mail."""

    @patch("apps.core.services.email_service.enviar_email_task.delay")
    def test_deve_enviar_email_sem_anexos(self, delay_mock):
        """Deve solicitar o envio do e-mail sem anexos."""
        EmailService.enviar(
            assunto="Teste",
            template="emails/teste.html",
            contexto={"nome": "João"},
            destinatarios=["teste@email.com"],
        )

        delay_mock.assert_called_once_with(
            assunto="Teste",
            template="emails/teste.html",
            contexto={"nome": "João"},
            destinatarios=["teste@email.com"],
            anexos=[],
        )

    @patch("apps.core.services.email_service.enviar_email_task.delay")
    def test_deve_enviar_email_com_anexos(self, delay_mock):
        """Deve solicitar o envio do e-mail com anexos."""
        anexos = [
            {
                "nome": "arquivo.pdf",
                "conteudo": b"pdf",
                "tipo_conteudo": "application/pdf",
            }
        ]

        EmailService.enviar(
            assunto="Teste",
            template="emails/teste.html",
            contexto={},
            destinatarios=["teste@email.com"],
            anexos=anexos,
        )

        delay_mock.assert_called_once_with(
            assunto="Teste",
            template="emails/teste.html",
            contexto={},
            destinatarios=["teste@email.com"],
            anexos=anexos,
        )
