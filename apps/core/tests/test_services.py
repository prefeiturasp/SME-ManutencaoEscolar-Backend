"""Testes unitários para o serviço de autenticação EOL."""

import json
from unittest.mock import Mock, patch

import pytest
import requests

from apps.core.constants import (
    ENDPOINT_USUARIO_EXISTE_CORESSO,
)
from apps.core.exceptions import (
    FalhaAutenticacaoError,
    InternalError,
    SmeIntegracaoError,
)
from apps.core.services.autenticacao_eol_service import AutenticacaoEOLService


class TestAutenticacaoEOLService:
    """Testes para a classe AutenticacaoEOLService."""

    # Constantes para os testes
    LOGIN_VALIDO = "1234567"
    SENHA_VALIDA = "senha123"
    TOKEN = "fake-token"
    URL_BASE = "https://api.exemplo"

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_sucesso(self, mock_autentica_usuario):
        """Deve retornar sucesso na autenticação."""
        response_data = {"nome": "Usuário Teste", "rf": self.LOGIN_VALIDO}
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = response_data
        mock_autentica_usuario.return_value = mock_response

        resultado = AutenticacaoEOLService.autentica(
            self.LOGIN_VALIDO, self.SENHA_VALIDA
        )

        assert resultado == response_data
        mock_autentica_usuario.assert_called_once()
        args, kwargs = mock_autentica_usuario.call_args
        assert json.loads(
            kwargs.get("data", args[2] if len(args) > 2 else "")
        ) == {
            "login": self.LOGIN_VALIDO,
            "senha": self.SENHA_VALIDA,
        }

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    def test_autentica_credenciais_vazias(self):
        """Deve lançar FalhaAutenticacaoError quan login/senha são vazios."""
        with pytest.raises(
            FalhaAutenticacaoError,
            match="Os campos login e senha são obrigatórios",
        ):
            AutenticacaoEOLService.autentica("", self.SENHA_VALIDA)

        with pytest.raises(
            FalhaAutenticacaoError,
            match="Os campos login e senha são obrigatórios",
        ):
            AutenticacaoEOLService.autentica(self.LOGIN_VALIDO, "")

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    def test_autentica_credenciais_tipo_invalido(self):
        """Deve lançar FalhaAutenticacaoError."""
        with pytest.raises(
            FalhaAutenticacaoError,
            match="As credenciais informadas são inválidas",
        ):
            AutenticacaoEOLService.autentica(1234567, self.SENHA_VALIDA)

        # Act & Assert - Senha não é string
        with pytest.raises(
            FalhaAutenticacaoError,
            match="As credenciais informadas são inválidas",
        ):
            AutenticacaoEOLService.autentica(self.LOGIN_VALIDO, 12345)

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    def test_autentica_sem_url_configurada(self):
        """Deve lançar InternalError."""
        with (
            patch(
                "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL",
                "",
            ),
            pytest.raises(
                InternalError, match="Serviço de autenticação não configurado"
            ),
        ):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    def test_autentica_sem_token_configurado(self):
        """Deve lançar InternalError para token do EOL não está configurado."""
        with (
            patch(
                "apps.core.services.autenticacao_eol_service."
                "SME_API_EOL_TOKEN",
                "",
            ),
            pytest.raises(
                InternalError, match="Serviço de autenticação não configurado"
            ),
        ):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_erro_401(self, mock_autentica_usuario):
        """Deve lançar FalhaAutenticacaoError quando a API retorna 401."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 401
        mock_response.ok = False
        mock_autentica_usuario.return_value = mock_response

        with pytest.raises(
            FalhaAutenticacaoError,
            match="Não foi possível autenticar o usuário",
        ):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_erro_429_rate_limit(self, mock_autentica_usuario):
        """Deve lançar SmeIntegracaoError quando a API retorna 429."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 429
        mock_response.ok = False
        mock_autentica_usuario.return_value = mock_response

        # Act & Assert
        with pytest.raises(
            SmeIntegracaoError, match="muitas tentativas de autenticação"
        ):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_erro_http_geral(self, mock_autentica_usuario):
        """Deve lançar SmeIntegracaoError para outros erros HTTP (ex: 500)."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.ok = False
        mock_response.text = "Internal Server Error"
        mock_autentica_usuario.return_value = mock_response

        with pytest.raises(
            SmeIntegracaoError,
            match="Não foi possível concluir a autenticação",
        ):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_resposta_json_invalido(self, mock_autentica_usuario):
        """Deve lançar SmeIntegracaoError."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_autentica_usuario.return_value = mock_response

        with pytest.raises(SmeIntegracaoError, match="resposta inválida"):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_timeout(self, mock_autentica_usuario):
        """Deve lançar SmeIntegracaoError."""
        mock_autentica_usuario.side_effect = requests.exceptions.Timeout()
        with pytest.raises(
            SmeIntegracaoError, match="demorou mais do que o esperado"
        ):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_erro_conexao(self, mock_autentica_usuario):
        """Deve lançar SmeIntegracaoError quando ocorre erro de conexão."""
        mock_autentica_usuario.side_effect = (
            requests.exceptions.ConnectionError()
        )
        with pytest.raises(
            SmeIntegracaoError, match="Não foi possível acessar o serviço"
        ):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_erro_requisicao_generico(self, mock_autentica_usuario):
        """Deve lançar SmeIntegracaoError para outros erros de requisição."""
        mock_autentica_usuario.side_effect = (
            requests.exceptions.RequestException()
        )
        with pytest.raises(SmeIntegracaoError, match="falha na comunicação"):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_erro_inesperado(self, mock_autentica_usuario):
        """Deve lançar InternalError para exceções não mapeadas."""
        mock_autentica_usuario.side_effect = Exception("Erro desconhecido")
        with pytest.raises(
            InternalError, match="erro interno durante a autenticação"
        ):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_propaga_falha_autenticacao(
        self, mock_autentica_usuario
    ):
        """Deve propagar FalhaAutenticacaoError."""
        mock_autentica_usuario.side_effect = FalhaAutenticacaoError(
            "Erro de autenticação"
        )
        with pytest.raises(
            FalhaAutenticacaoError, match="Erro de autenticação"
        ):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_autentica_propaga_sme_integracao_error(
        self, mock_autentica_usuario
    ):
        """Deve propagar SmeIntegracaoError sem capturar como erro genérico."""
        mock_autentica_usuario.side_effect = SmeIntegracaoError(
            "Erro de integração"
        )

        with pytest.raises(SmeIntegracaoError, match="Erro de integração"):
            AutenticacaoEOLService.autentica(
                self.LOGIN_VALIDO, self.SENHA_VALIDA
            )

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "usuario_existe"
    )
    def test_usuario_existe_no_coresso_sucesso(self, mock_usuario_existe):
        """Deve retornar True quando o usuário existe no CoreSSO (HTTP 200)."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_usuario_existe.return_value = mock_response

        resultado = AutenticacaoEOLService.usuario_existe_no_coresso(
            self.LOGIN_VALIDO
        )

        assert resultado is True
        mock_usuario_existe.assert_called_once()
        args, _ = mock_usuario_existe.call_args
        assert self.URL_BASE + ENDPOINT_USUARIO_EXISTE_CORESSO in args

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "usuario_existe"
    )
    def test_usuario_existe_no_coresso_nao_encontrado(
        self, mock_usuario_existe
    ):
        """Deve retornar False quando o usuário não existe no CoreSSO."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_usuario_existe.return_value = mock_response

        resultado = AutenticacaoEOLService.usuario_existe_no_coresso(
            self.LOGIN_VALIDO
        )

        assert resultado is False

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "usuario_existe"
    )
    def test_usuario_existe_no_coresso_erro_servidor(
        self, mock_usuario_existe
    ):
        """Deve retornar False para qualquer código diferente de 200."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_usuario_existe.return_value = mock_response
        resultado = AutenticacaoEOLService.usuario_existe_no_coresso(
            self.LOGIN_VALIDO
        )
        assert resultado is False

    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL", URL_BASE
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN", TOKEN
    )
    @patch(
        "apps.core.services.autenticacao_eol_service.ApiEOLRepository."
        "autentica_usuario"
    )
    def test_headers_corretos_na_requisicao(self, mock_autentica_usuario):
        """Deve enviar os headers corretos na requisição de autenticação."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {}
        mock_autentica_usuario.return_value = mock_response
        AutenticacaoEOLService.autentica(self.LOGIN_VALIDO, self.SENHA_VALIDA)
        args, kwargs = mock_autentica_usuario.call_args
        headers = kwargs.get("headers", args[1] if len(args) > 1 else {})
        assert headers.get("x-api-eol-key") == self.TOKEN
        assert headers.get("Content-Type") == "application/json-patch+json"
        assert headers.get("accept") == "application/json"


class TestValidaCredenciais:
    """Testes específicos para o método _valida_credenciais."""

    def test_valida_credenciais_validas(self):
        """Não deve lançar exceção para credenciais válidas."""
        AutenticacaoEOLService._valida_credenciais("1234567", "senha123")

    def test_valida_credenciais_none(self):
        """Deve lançar FalhaAutenticacaoError quando credenciais são None."""
        with pytest.raises(FalhaAutenticacaoError):
            AutenticacaoEOLService._valida_credenciais(None, "senha123")

        # Act & Assert - Senha None
        with pytest.raises(FalhaAutenticacaoError):
            AutenticacaoEOLService._valida_credenciais("1234567", None)

    def test_valida_credenciais_boolean(self):
        """Deve lançar FalhaAutenticacaoError."""
        with pytest.raises(
            FalhaAutenticacaoError,
            match="As credenciais informadas são inválidas",
        ):
            AutenticacaoEOLService._valida_credenciais(True, "senha123")


class TestValidaUrl:
    """Testes específicos para o método _valida_url."""

    def test_valida_url_configurada(self):
        """Não deve lançar exceção quando a URL está configurada."""
        with patch(
            "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL",
            "https://api.exemplo.com",
        ):
            AutenticacaoEOLService._valida_url()

    def test_valida_url_vazia(self):
        """Deve lançar InternalError quando a URL está vazia."""
        with (
            patch(
                "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL",
                "",
            ),
            pytest.raises(
                InternalError, match="Serviço de autenticação não configurado"
            ),
        ):
            AutenticacaoEOLService._valida_url()

    def test_valida_url_none(self):
        """Deve lançar InternalError quando a URL é None."""
        with (
            patch(
                "apps.core.services.autenticacao_eol_service.SME_API_EOL_URL",
                None,
            ),
            pytest.raises(
                InternalError, match="Serviço de autenticação não configurado"
            ),
        ):
            AutenticacaoEOLService._valida_url()


class TestObterHeaders:
    """Testes específicos para o método _obter_headers."""

    def test_obter_headers_sucesso(self):
        """Deve retornar os headers corretos."""
        chave = "meu-chave-seguro"
        with patch(
            "apps.core.services.autenticacao_eol_service.SME_API_EOL_TOKEN",
            chave,
        ):
            headers = AutenticacaoEOLService._obter_headers()
            assert headers == {
                "accept": "application/json",
                "x-api-eol-key": chave,
                "Content-Type": "application/json-patch+json",
            }

    def test_obter_headers_sem_token(self):
        """Deve lançar InternalError quando o token não está configurado."""
        with (
            patch(
                "apps.core.services.autenticacao_eol_service."
                "SME_API_EOL_TOKEN",
                "",
            ),
            pytest.raises(
                InternalError, match="Serviço de autenticação não configurado"
            ),
        ):
            AutenticacaoEOLService._obter_headers()

    def test_obter_headers_token_none(self):
        """Deve lançar InternalError quando o token é None."""
        with (
            patch(
                "apps.core.services.autenticacao_eol_service."
                "SME_API_EOL_TOKEN",
                None,
            ),
            pytest.raises(
                InternalError, match="Serviço de autenticação não configurado"
            ),
        ):
            AutenticacaoEOLService._obter_headers()


class TestTratarResposta:
    """Testes específicos para o método _tratar_resposta."""

    LOGIN = "1234567"

    def test_tratar_resposta_sucesso(self):
        """Deve retornar os dados JSON quando a resposta é bem-sucedida."""
        response_data = {"nome": "Teste", "rf": self.LOGIN}
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = response_data

        resultado = AutenticacaoEOLService._tratar_resposta(
            mock_response, self.LOGIN
        )

        assert resultado == response_data

    def test_tratar_resposta_erro_401(self):
        """Deve lançar FalhaAutenticacaoError para status 401."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 401

        with pytest.raises(
            FalhaAutenticacaoError,
            match="Não foi possível autenticar o usuário",
        ):
            AutenticacaoEOLService._tratar_resposta(mock_response, self.LOGIN)

    def test_tratar_resposta_erro_429(self):
        """Deve lançar SmeIntegracaoError para status 429."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 429

        with pytest.raises(
            SmeIntegracaoError, match="muitas tentativas de autenticação"
        ):
            AutenticacaoEOLService._tratar_resposta(mock_response, self.LOGIN)

    def test_tratar_resposta_erro_500(self):
        """Deve lançar SmeIntegracaoError para outros erros HTTP."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.ok = False
        mock_response.text = "Erro interno"

        with pytest.raises(
            SmeIntegracaoError,
            match="Não foi possível concluir a autenticação",
        ):
            AutenticacaoEOLService._tratar_resposta(mock_response, self.LOGIN)

    def test_tratar_resposta_json_invalido(self):
        """Deve lançar SmeIntegracaoError quando o JSON é inválido."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.side_effect = ValueError("JSON inválido")

        with pytest.raises(SmeIntegracaoError, match="resposta inválida"):
            AutenticacaoEOLService._tratar_resposta(mock_response, self.LOGIN)
