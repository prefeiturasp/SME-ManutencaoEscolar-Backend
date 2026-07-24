from unittest.mock import patch

from apps.core.services.token_service import TokenService


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
