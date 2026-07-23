"""Repositório responsável pelo acesso aos dados da aplicação EOL."""

import logging
from typing import Any

import requests
from rest_framework import status

from apps.core.exceptions import FalhaAutenticacaoError, SmeIntegracaoError

logger = logging.getLogger(__name__)


class ApiEOLRepository:
    """Repositório responsável pela comunicação com o serviço EOL."""

    @staticmethod
    def post(
        url: str, headers: dict[str, str], data: str
    ) -> requests.Response:
        """
        Realiza uma requisição POST ao serviço EOL.

        Args:
            url (str): URL completa do endpoint.
            headers (dict[str, str]): Cabeçalhos HTTP enviados na requisição.
            data (str): Corpo da requisição serializado em JSON.

        Returns:
            requests.Response: Resposta HTTP retornada pelo serviço
                EOL.
        """
        return requests.post(
            url,
            headers=headers,
            data=data,
            timeout=10,
        )

    @staticmethod
    def get(url: str, headers: dict[str, str]) -> requests.Response:
        """
        Realiza uma requisição GET ao serviço EOL.

        Args:
            url (str): URL completa do endpoint.
            headers (dict[str, str]): Cabeçalhos HTTP enviados na requisição.

        Returns:
            requests.Response: Resposta HTTP retornada pelo serviço
                EOL.
        """
        return requests.get(
            url,
            headers=headers,
            timeout=10,
        )

    @classmethod
    def autentica_usuario(
        cls, url: str, headers: dict[str, str], data: str
    ) -> dict:
        response = cls.post(url, headers=headers, data=data)
        return cls._tratar_resposta(response)

    @staticmethod
    def usuario_existe(
        url: str, headers: dict[str, str], files: dict[str, tuple[None, str]]
    ) -> requests.Response:
        return requests.post(
            url,
            headers=headers,
            files=files,
            timeout=10,
        )

    @classmethod
    def buscar_cargos(cls, url: str, headers: dict[str, str]) -> list:
        """
        Consulta a API do EOL para obter a lista de cargos disponíveis.

        Realiza uma requisição HTTP GET para o endpoint informado e retorna
        o conteúdo da resposta em formato JSON. Caso a API retorne um status
        diferente de HTTP 200 (OK), registra o erro em log e lança uma
        exceção de integração.

        Args:
            url (str):  URL do endpoint da API do EOL responsável pela
                consulta dos cargos.
            headers (dict[str, str]):  Cabeçalhos HTTP necessários para
                autenticação e acesso
            à API.

        Raises:
            SmeIntegracaoError: Caso a API do EOL retorne um status diferente
            de HTTP 200 (OK).

        Returns:
            list: Conteúdo da resposta da API convertido para uma lista.
        """
        response = cls.get(url=url, headers=headers)

        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "Erro ao consultar cargos. Status: %s | Body: %s",
                response.status_code,
                response.text,
            )
            raise SmeIntegracaoError("Erro ao consultar cargos do servidor")
        dados: list = response.json()
        return dados

    @staticmethod
    def _tratar_resposta(response: requests.Response) -> dict[str, Any]:
        """
        Processa a resposta retornada pelo serviço de autenticação EOL.

        Args:
            response (requests.Response): Resposta HTTP retornada pela API.
            login (object): Login utilizado na tentativa de autenticação.

        Raises:
            FalhaAutenticacaoError:  Quando as credenciais informadas são
                inválidas (HTTP 401).
            SmeIntegracaoError: Quando o limite de tentativas é excedido
                (HTTP 429), ocorre qualquer outro erro retornado pela API ou
                a resposta possui formato inválido.

        Returns:
            dict[str, Any]: Conteúdo da resposta convertido para dicionário.
        """
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            logger.warning("Credenciais inválidas")
            raise FalhaAutenticacaoError(
                "Não foi possível autenticar o usuário. Verifique o login e "
                "a senha informados."
            )

        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            logger.warning("Rate limit atingido")
            raise SmeIntegracaoError(
                "Foram realizadas muitas tentativas de autenticação. Aguarde "
                "alguns minutos antes de tentar novamente."
            )

        if not response.ok:
            logger.error(
                "Erro HTTP %s ao autenticar. Resposta: %s",
                response.status_code,
                response.text[:200],
            )
            raise SmeIntegracaoError(
                "Não foi possível concluir a autenticação no momento."
            )

        try:
            response_data: dict[str, Any] = response.json()
        except ValueError as err:
            logger.exception(
                "Resposta inválida do EOL: %s",
                str(err),
            )
            raise SmeIntegracaoError(
                "O serviço de autenticação retornou uma resposta inválida."
            ) from err

        return response_data

    @classmethod
    def obter_dados_usuarios(
        cls, url: str, headers: dict[str, str]
    ) -> dict[str, str]:
        """Consulta a API do EOL para obter os dados de um usuário.

        Realiza uma requisição HTTP GET para o endpoint informado e retorna
        o conteúdo da resposta em formato JSON. Caso a API retorne um status
        diferente de HTTP 200 (OK), registra o erro em log e lança uma
        exceção de integração.

        Args:
            url (str):  URL do endpoint da API do EOL responsável pela
                consulta dos dados do usuário.
            headers (dict[str, str]): Cabeçalhos HTTP necessários para
                autenticação e acesso à API.

        Raises:
            SmeIntegracaoError: Caso a API do EOL retorne um status diferente
            de HTTP 200 (OK).

        Returns:
            dict[str, str]: Dados do usuário retornados pela API.
        """
        response = cls.get(url=url, headers=headers)

        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "Erro ao consultar dados. Status: %s | Body: %s",
                response.status_code,
                response.text,
            )
            raise SmeIntegracaoError("Erro ao consultar dados do servidor")
        dados: dict = response.json()
        return dados
