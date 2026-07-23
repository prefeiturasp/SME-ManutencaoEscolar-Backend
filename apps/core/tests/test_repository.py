from unittest.mock import Mock, patch

import pytest
import requests

from apps.core.exceptions import FalhaAutenticacaoError, SmeIntegracaoError
from apps.core.repository.autenticacao_eol_repository import ApiEOLRepository

URL = "http://teste"


class TestApiEOLRepository:
    """Testes para a classe ApiEOLRepository."""

    URL = "https://api.exemplo/api/autenticacao"
    HEADERS = {
        "accept": "application/json",
        "x-api-eol-key": "fake-token",
        "Content-Type": "application/json-patch+json",
    }
    DATA = '{"login": "1234567", "senha": "senha123"}'

    @patch("apps.core.repository.autenticacao_eol_repository.requests.post")
    def test_post_realiza_requisicao_com_parametros_corretos(self, mock_post):
        """Deve realizar requisição POST com URL, headers, data e timeout."""
        mock_response = Mock(spec=requests.Response)
        mock_post.return_value = mock_response

        resultado = ApiEOLRepository.post(
            url=self.URL, headers=self.HEADERS, data=self.DATA
        )

        assert resultado == mock_response
        mock_post.assert_called_once_with(
            self.URL,
            headers=self.HEADERS,
            data=self.DATA,
            timeout=10,
        )

    @patch("apps.core.repository.autenticacao_eol_repository.requests.post")
    def test_post_retorna_response_do_servico(self, mock_post):
        """Deve retornar o objeto Response da biblioteca requests."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        resultado = ApiEOLRepository.post(
            url=self.URL, headers=self.HEADERS, data=self.DATA
        )

        assert resultado.status_code == 200
        assert isinstance(resultado, requests.Response)

    @patch.object(ApiEOLRepository, "post")
    def test_autentica_usuario_chama_metodo_post(self, mock_post):
        """Deve delegar a chamada de autenticação para o método post."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {"token": "fake-token"}
        mock_post.return_value = mock_response

        resultado = ApiEOLRepository.autentica_usuario(
            url=self.URL, headers=self.HEADERS, data=self.DATA
        )

        assert resultado == {"token": "fake-token"}
        mock_post.assert_called_once_with(
            self.URL, headers=self.HEADERS, data=self.DATA
        )

    @patch("apps.core.repository.autenticacao_eol_repository.requests.post")
    def test_usuario_existe_realiza_requisicao_com_arquivos(self, mock_post):
        """Deve realizar requisição POST com files para verificar usuário."""
        mock_response = Mock(spec=requests.Response)
        mock_post.return_value = mock_response
        files = {"usuario": (None, "1234567")}

        resultado = ApiEOLRepository.usuario_existe(
            url=self.URL, headers=self.HEADERS, files=files
        )

        assert resultado == mock_response
        mock_post.assert_called_once_with(
            self.URL,
            headers=self.HEADERS,
            files=files,
            timeout=10,
        )

    @patch("apps.core.repository.autenticacao_eol_repository.requests.post")
    def test_post_propaga_excecoes_de_requests(self, mock_post):
        """Deve propagar exceções da biblioteca requests sem tratamento."""
        mock_post.side_effect = requests.exceptions.Timeout("Tempo excedido")

        with pytest.raises(
            requests.exceptions.Timeout, match="Tempo excedido"
        ):
            ApiEOLRepository.post(
                url=self.URL, headers=self.HEADERS, data=self.DATA
            )

    @patch("apps.core.repository.autenticacao_eol_repository.requests.post")
    def test_post_com_timeout_padrao_de_10_segundos(self, mock_post):
        """Deve usar timeout padrão de 10 segundos na requisição."""
        mock_response = Mock(spec=requests.Response)
        mock_post.return_value = mock_response

        ApiEOLRepository.post(
            url=self.URL, headers=self.HEADERS, data=self.DATA
        )

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["timeout"] == 10

    @patch("apps.core.repository.autenticacao_eol_repository.requests.post")
    def test_usuario_existe_com_timeout_padrao_de_10_segundos(self, mock_post):
        """Deve usar timeout de 10 segundos na verificação de usuário."""
        mock_response = Mock(spec=requests.Response)
        mock_post.return_value = mock_response
        files = {"usuario": (None, "1234567")}

        ApiEOLRepository.usuario_existe(
            url=self.URL, headers=self.HEADERS, files=files
        )

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["timeout"] == 10

    @patch("apps.core.repository.autenticacao_eol_repository.requests.post")
    def test_post_erro_de_conexao(self, mock_post):
        """Deve propagar ConnectionError sem tratamento adicional."""
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Falha na conexão"
        )

        with pytest.raises(
            requests.exceptions.ConnectionError, match="Falha na conexão"
        ):
            ApiEOLRepository.post(
                url=self.URL, headers=self.HEADERS, data=self.DATA
            )

    @patch("apps.core.repository.autenticacao_eol_repository.requests.get")
    def test_get(self, mock_get):
        response = Mock()
        mock_get.return_value = response

        resultado = ApiEOLRepository.get(
            url=URL,
            headers={"Authorization": "Bearer token"},
        )

        assert resultado is response

        mock_get.assert_called_once_with(
            URL,
            headers={"Authorization": "Bearer token"},
            timeout=10,
        )

    @patch.object(ApiEOLRepository, "get")
    def test_buscar_cargos(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.json.return_value = [{"cargoBase": "Diretor"}]

        mock_get.return_value = response

        resultado = ApiEOLRepository.buscar_cargos(
            url=URL,
            headers={},
        )

        assert resultado == [{"cargoBase": "Diretor"}]

        mock_get.assert_called_once_with(
            url=URL,
            headers={},
        )

        response.json.assert_called_once()

    @patch.object(ApiEOLRepository, "get")
    def test_buscar_cargos_erro(self, mock_get):
        response = Mock()
        response.status_code = 500
        response.text = "Erro interno"

        mock_get.return_value = response

        with pytest.raises(
            SmeIntegracaoError,
            match="Erro ao consultar cargos do servidor",
        ):
            ApiEOLRepository.buscar_cargos(
                url=URL,
                headers={},
            )

        mock_get.assert_called_once_with(
            url=URL,
            headers={},
        )

    @patch.object(ApiEOLRepository, "get")
    def test_obter_dados_usuario(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"nome": "João"}

        mock_get.return_value = response

        resultado = ApiEOLRepository.obter_dados_usuarios(
            url=URL,
            headers={},
        )

        assert resultado == {"nome": "João"}

        mock_get.assert_called_once_with(
            url=URL,
            headers={},
        )

        response.json.assert_called_once()

    @patch.object(ApiEOLRepository, "get")
    def test_obter_dados_usuario_erro(self, mock_get):
        response = Mock()
        response.status_code = 500
        response.text = "Erro interno"

        mock_get.return_value = response

        with pytest.raises(
            SmeIntegracaoError,
            match="Erro ao consultar dados do servidor",
        ):
            ApiEOLRepository.obter_dados_usuarios(
                url=URL,
                headers={},
            )

    def test_tratar_resposta_200(self):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"ok": True}

        resultado = ApiEOLRepository._tratar_resposta(response)

        assert resultado == {"ok": True}

    def test_tratar_resposta_401(self):
        response = Mock()
        response.status_code = 401

        with pytest.raises(FalhaAutenticacaoError):
            ApiEOLRepository._tratar_resposta(response)

    def test_tratar_resposta_429(self):
        response = Mock()
        response.status_code = 429

        with pytest.raises(SmeIntegracaoError):
            ApiEOLRepository._tratar_resposta(response)

    def test_tratar_resposta_500(self):
        response = Mock()
        response.status_code = 500
        response.ok = False
        response.text = "Erro"

        with pytest.raises(SmeIntegracaoError):
            ApiEOLRepository._tratar_resposta(response)

    def test_tratar_resposta_json_invalido(self):
        response = Mock()
        response.status_code = 200
        response.json.side_effect = ValueError()

        with pytest.raises(SmeIntegracaoError):
            ApiEOLRepository._tratar_resposta(response)


class TestApiEOLRepositoryIntegracao:
    """Testes que verificam a integração entre os métodos."""

    def test_metodo_post_aceita_parametros_nomeados(self):
        """Os parâmetros devem ser passados como keyword arguments."""
        import inspect

        assinatura = inspect.signature(ApiEOLRepository.post)
        parametros = list(assinatura.parameters.keys())

        assert "url" in parametros
        assert "headers" in parametros
        assert "data" in parametros
