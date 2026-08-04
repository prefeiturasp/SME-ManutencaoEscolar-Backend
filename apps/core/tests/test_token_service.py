from unittest.mock import MagicMock, patch

import pytest
from rest_framework_simplejwt.exceptions import TokenError

from apps.core.exceptions import TokenInvalidoError
from apps.core.services.token_service import TokenService
from apps.usuarios.exceptions import UsuarioNaoEncontradoError


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
        "usuario_existe_por_id"
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
        mock_usuario_existe.return_value = True

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
    def test_atualizar_token_token_invalido(self, mock_refresh_token):
        mock_refresh_token.side_effect = TokenError("token inválido")

        with pytest.raises(TokenError):
            TokenService.atualizar_token("refresh-token")

    @patch("apps.core.services.token_service.RefreshToken")
    def test_logout_com_sucesso(self, mock_refresh_token):
        token = MagicMock()
        token.__getitem__.return_value = 10

        mock_refresh_token.return_value = token

        TokenService.logout(10, "refresh-token")

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
