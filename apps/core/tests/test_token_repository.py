from unittest.mock import MagicMock, patch

from apps.core.repository.token_repository import TokenRepository


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
