from unittest.mock import MagicMock, patch

import pytest
from django.db.models import ObjectDoesNotExist
from rest_framework_simplejwt.exceptions import TokenError

from apps.core.exceptions import TokenInvalidoError
from apps.core.services.token_service import TokenService
from apps.usuarios.exceptions import UsuarioNaoEncontradoError

pytestmark = pytest.mark.django_db


class TestTokenService:
    @patch("apps.core.services.token_service.TokenRepository.gerar_tokens")
    def test_gerar_tokens(self, mock_gerar_tokens):
        retorno = {
            "access": "access-token",
            "refresh": "refresh-token",
        }

        mock_gerar_tokens.return_value = retorno

        resultado = TokenService.gerar_tokens(10)

        assert resultado == retorno
        mock_gerar_tokens.assert_called_once_with(10)

    @patch(
        "apps.core.services.token_service.UsuarioRepository."
        "retorna_username_usuario"
    )
    @patch("apps.core.services.token_service.RefreshToken")
    def test_atualizar_token_com_sucesso(
        self,
        mock_refresh_token,
        mock_usuario_existe,
    ):
        token = MagicMock()
        token.__getitem__.return_value = 10

        mock_refresh_token.return_value = token
        mock_usuario_existe.return_value = {"usermame": "username"}

        TokenService.atualizar_token("refresh-token")

        mock_refresh_token.assert_called_once_with("refresh-token")
        mock_usuario_existe.assert_called_once_with(10)

    @patch(
        "apps.core.services.token_service.UsuarioRepository."
        "usuario_existe_por_id"
    )
    @patch("apps.core.services.token_service.RefreshToken")
    def test_atualizar_token_usuario_nao_encontrado(
        self,
        mock_refresh_token,
        mock_usuario_existe,
    ):
        token = MagicMock()
        token.__getitem__.return_value = 10

        mock_refresh_token.return_value = token
        mock_usuario_existe.return_value = False

        with pytest.raises(UsuarioNaoEncontradoError):
            TokenService.atualizar_token("refresh-token")

    @patch("apps.core.services.token_service.RefreshToken")
    def test_atualizar_token_com_token_invalido(self, mock_refresh_token):
        mock_refresh_token.side_effect = TokenError("token inválido")

        with pytest.raises(TokenInvalidoError):
            TokenService.atualizar_token("refresh-token")

    @patch("apps.core.services.token_service.RefreshToken")
    def test_logout_com_sucesso(self, mock_refresh_token, usuario_ativo):
        id_usuario = usuario_ativo.id
        token = MagicMock()
        token.__getitem__.return_value = id_usuario

        mock_refresh_token.return_value = token

        TokenService.logout(id_usuario, "refresh-token")

        token.blacklist.assert_called_once()

    @patch("apps.core.services.token_service.RefreshToken")
    def test_logout_token_de_outro_usuario(self, mock_refresh_token):
        token = MagicMock()
        token.__getitem__.return_value = 20

        mock_refresh_token.return_value = token

        with pytest.raises(TokenInvalidoError) as exc:
            TokenService.logout(10, "refresh-token")

        assert exc.value.title == "Logout não realizado."
        assert exc.value.detail == (
            "O token não pertence ao usuário autenticado."
        )

        token.blacklist.assert_not_called()

    @patch("apps.core.services.token_service.RefreshToken")
    def test_logout_token_invalido(self, mock_refresh_token):
        mock_refresh_token.side_effect = TokenError("token inválido")

        with pytest.raises(TokenInvalidoError) as exc:
            TokenService.logout(10, "refresh-token")

        assert exc.value.title == "Logout não realizado."
        assert (
            exc.value.detail
            == "O refresh token é inválido ou já foi revogado."
        )

    @patch(
        "apps.core.services.token_service.TokenRepository."
        "verificar_token_atualizar_senha"
    )
    def test_validar_token(self, verificar_token_mock, usuario_ativo_dict):
        """Deve validar o token de recuperação de senha."""
        username = usuario_ativo_dict["username"]
        token = "token-123"

        TokenService.validar_token_recuperar_senha(
            username=username,
            token=token,
        )

        verificar_token_mock.assert_called_once_with(
            username=username,
            token=token,
        )

    @patch(
        "apps.core.services.token_service.TokenRepository."
        "verificar_token_atualizar_senha"
    )
    def test_validar_token_usuario_nao_encontrado(self, verificar_token_mock):
        """Deve lançar erro quando o usuário não for encontrado."""
        verificar_token_mock.side_effect = ObjectDoesNotExist

        with pytest.raises(UsuarioNaoEncontradoError) as exc:
            TokenService.validar_token_recuperar_senha(
                username="1234567",
                token="token-123",
            )

        assert exc.value.title == "Usuário não encontrado."
        assert exc.value.detail == "Usuário não encontrado ou inválido"

        verificar_token_mock.assert_called_once_with(
            username="1234567",
            token="token-123",
        )

    @patch(
        "apps.core.services.token_service.TokenRepository."
        "verificar_token_atualizar_senha"
    )
    def test_validar_token_invalido(self, verificar_token_mock):
        """Deve lançar erro quando o token for inválido ou expirado."""
        verificar_token_mock.side_effect = TokenInvalidoError(
            title="Token inválido.",
            detail="Token inválido.",
        )

        with pytest.raises(TokenInvalidoError) as exc:
            TokenService.validar_token_recuperar_senha(
                username="1234567",
                token="token-invalido",
            )

        assert exc.value.title == "O link está expirado!"
        assert (
            exc.value.detail
            == "Por segurança, o link de redefinição tem validade de "
            "6 horas. Solicite um novo para redefinir sua senha."
        )

        verificar_token_mock.assert_called_once_with(
            username="1234567",
            token="token-invalido",
        )
