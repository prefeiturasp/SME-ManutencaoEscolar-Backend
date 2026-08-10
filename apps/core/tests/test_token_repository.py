from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from apps.core.exceptions import TokenInvalidoError
from apps.core.repository.token_repository import TokenRepository

pytestmark = pytest.mark.django_db


class TestTokenRepository:
    @patch("apps.core.repository.token_repository.RefreshToken.for_user")
    @patch("apps.core.repository.token_repository.Usuario.objects.get")
    def test_gerar_tokens(
        self,
        mock_usuario_get,
        mock_refresh_for_user,
    ):
        usuario = MagicMock()
        mock_usuario_get.return_value = usuario

        refresh = MagicMock()
        refresh.access_token = "access-token"

        mock_refresh_for_user.return_value = refresh

        resultado = TokenRepository.gerar_tokens(1)

        mock_usuario_get.assert_called_once_with(pk=1)
        mock_refresh_for_user.assert_called_once_with(usuario)

        assert resultado == {
            "refresh": str(refresh),
            "access": "access-token",
        }

        @patch(
            "apps.core.repository.token_repository.PasswordResetTokenGenerator"
        )
        def test_deve_gerar_token(
            self, consulta_mock, token_generator_mock, usuario_ativo
        ):
            consulta_mock.return_value = usuario_ativo

            instancia = MagicMock()
            instancia.make_token.return_value = "token-123"

            token_generator_mock.return_value = instancia

            resultado = TokenRepository.gerar_token_recuperar_senha(
                usuario_ativo.username
            )

            assert resultado == {"token_recuperacao": "token-123"}

            consulta_mock.assert_called_once_with(usuario_ativo.username)
            instancia.make_token.assert_called_once_with(usuario_ativo)

    @patch("apps.core.repository.token_repository.PasswordResetTokenGenerator")
    def test_verificar_token_atualizar_senha_token_invalido(
        self, token_generator_mock, usuario_ativo
    ):
        """Deve lançar exceção quando o token for inválido."""
        instancia = MagicMock()
        instancia.check_token.return_value = False

        token_generator_mock.return_value = instancia

        with pytest.raises(TokenInvalidoError) as exc:
            TokenRepository.verificar_token_atualizar_senha(
                usuario_ativo.username,
                "token-invalido",
            )

        assert exc.value.title == "Token inválido."
        assert (
            exc.value.detail
            == "O token de recuperação de senha é inválido ou expirou."
        )

        instancia.check_token.assert_called_once_with(
            usuario_ativo,
            "token-invalido",
        )

    @patch("apps.core.repository.token_repository.PasswordResetTokenGenerator")
    def test_verificar_token_atualizar_senha_token_valido(
        self, token_generator_mock, usuario_ativo
    ):
        """Deve validar o token de recuperação de senha."""
        instancia = MagicMock()
        instancia.check_token.return_value = True

        token_generator_mock.return_value = instancia

        TokenRepository.verificar_token_atualizar_senha(
            usuario_ativo.username,
            "token-123",
        )
        instancia.check_token.assert_called_once_with(
            usuario_ativo,
            "token-123",
        )

    def test_invalidar_token_recuperacao_senha_invalida_token(
        self, usuario_ativo
    ):
        """Deve invalidar o token após alterar a senha."""
        token_generator = PasswordResetTokenGenerator()

        token = token_generator.make_token(usuario_ativo)
        assert token_generator.check_token(usuario_ativo, token)

        TokenRepository.invalidar_token_recuperacao_senha(
            usuario_ativo.username,
            "nova-senha-123",
        )

        usuario_ativo.refresh_from_db()

        assert not token_generator.check_token(usuario_ativo, token)
