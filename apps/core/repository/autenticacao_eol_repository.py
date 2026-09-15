"""Repositório responsável pelo acesso aos dados da aplicação EOL.

Este módulo centraliza as requisições HTTP realizadas pela aplicação ao
serviço EOL, incluindo autenticação, consulta de usuários e cargos,
verificação de existência de usuários e alteração de senha.

As operações de comunicação utilizam um timeout fixo de 10 segundos.
"""

import logging
from typing import Any

import requests
from rest_framework import status

from apps.core.exceptions import FalhaAutenticacaoError, SmeIntegracaoError

logger = logging.getLogger(__name__)


class ApiEOLRepository:
    """Centraliza a comunicação HTTP com o serviço EOL.

    O repositório encapsula as chamadas realizadas à API do EOL e concentra o
    tratamento das respostas HTTP relacionadas à integração. As operações
    disponibilizadas incluem:

        * autenticação de usuários;
        * consulta de cargos;
        * consulta de dados de usuários;
        * verificação da existência de usuários;
        * alteração de senha.

    As requisições HTTP possuem timeout de 10 segundos.
    """

    @staticmethod
    def post(
        url: str, headers: dict[str, str], data: str
    ) -> requests.Response:
        """
        Realiza uma requisição HTTP POST ao serviço EOL.

        Args:
            url (str): URL completa do endpoint do serviço EOL.
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
        Realiza uma requisição HTTP GET ao serviço EOL.

        Args:
            url (str): URL completa do endpoint do serviço EOL.
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
        """Autentica um usuário por meio da API do EOL.

        Realiza uma requisição POST para o endpoint de autenticação e delega o
        tratamento da resposta ao método :meth:`_tratar_resposta`.

        Args:
            url (str): URL do endpoint de autenticação.
            headers (dict[str, str]): Cabeçalhos HTTP necessários para
                autenticação.
            data (str): Corpo da requisição contendo os dados de autenticação,
                serializado conforme o formato esperado pela API.

        Returns:
            dict: Dados retornados pela API após uma autenticação bem-sucedida.

        Raises:
            FalhaAutenticacaoError: Se as credenciais forem inválidas
                (HTTP 401).
            SmeIntegracaoError: Se a API retornar HTTP 429, outro status HTTP
                de erro ou uma resposta JSON inválida.
        """
        response = cls.post(url, headers=headers, data=data)
        return cls._tratar_resposta(response)

    @staticmethod
    def usuario_existe(
        url: str, headers: dict[str, str], files: dict[str, tuple[None, str]]
    ) -> requests.Response:
        """Consulta a API do EOL para verificar a existência de um usuário.

        Realiza uma requisição POST enviando os dados por meio do parâmetro
        ``files``, conforme o formato esperado pelo endpoint utilizado.

        Args:
            url (str): URL do endpoint responsável pela consulta.
            headers (dict[str, str]): Cabeçalhos HTTP enviados na requisição.
            files (dict[str, tuple[None, str]]): Dados enviados na requisição
                multipart/form-data.

        Returns:
            requests.Response: Resposta HTTP retornada pela API do EOL.
        """
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

        Centraliza o tratamento dos principais cenários de resposta da API de
        autenticação:

        * HTTP 401: credenciais inválidas;
        * HTTP 429: limite de tentativas excedido;
        * demais respostas HTTP de erro: falha na integração;
        * resposta HTTP bem-sucedida com JSON inválido: resposta inválida do
        serviço.

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

    @staticmethod
    def alterar_senha(
        url: str, headers: dict[str, str], files: dict[str, tuple[None, str]]
    ) -> None:
        """Altera a senha do usuário por meio da API de integração.

        Realiza uma requisição HTTP POST para o endpoint informado, enviando
        os cabeçalhos e os dados da alteração de senha no formato
        multipart/form-data

        Args:
            url (str): URL do endpoint responsável pela alteração da senha.
            headers (dict[str, str]): Cabeçalhos HTTP utilizados na requisição.
            files (dict[str, tuple[None, str]]): Dados enviados na requisição
            multipart/form-data, contendo as informações necessárias para
            alteração da senha.

        Raises:
            FalhaAutenticacaoError: Levantada quando a API retorna HTTP 401,
                indicando falha na autenticação ou credenciais inválidas.
            SmeIntegracaoError: Levantada quando a API retorna um erro HTTP
                5xx, indicando uma falha no servidor da integração.
        """
        try:
            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=10,
            )
        except requests.exceptions.RequestException as exc:
            raise SmeIntegracaoError(
                "Erro de comunicação ao alterar a senha no servidor."
            ) from exc
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise FalhaAutenticacaoError(str(response.text))

        if response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise SmeIntegracaoError("Erro ao alterar a senha no servidor.")
