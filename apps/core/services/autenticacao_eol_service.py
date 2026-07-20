"""Serviços responsáveis pela autenticação de usuários no EOL."""

import json
import logging
from typing import Any

import requests
from rest_framework import status

from apps.core.constants import (
    ENDPOINT_AUTENTICACAO,
    ENDPOINT_USUARIO_EXISTE_CORESSO,
)
from apps.core.exceptions import (
    FalhaAutenticacaoError,
    InternalError,
    SmeIntegracaoError,
)
from apps.core.repository.autenticacao_eol_repository import ApiEOLRepository
from config.settings import SME_API_EOL_TOKEN, SME_API_EOL_URL

logger = logging.getLogger(__name__)


class AutenticacaoEOLService:
    """Serviço para autenticação de usuários no EOL."""

    @classmethod
    def autentica(cls, login: object, senha: object) -> dict[str, Any]:
        """
        Realiza a autenticação de um usuário no serviço EOL da SME.

        O método valida as credenciais informadas, monta a requisição para o
        endpoint de autenticação, envia a solicitação ao serviço externo e
        processa a resposta retornada.

        Args:
            login (object): Identificador do usuário (RF ou CPF).
            senha (object): Senha utilizada para autenticação.

        Returns:
            dict[str, Any]: Dados retornados pelo EOL após a autenticação
                bem-sucedida.

        Raises:
            FalhaAutenticacaoError:
                Caso o login ou a senha sejam inválidos ou as credenciais
                não atendam às validações de entrada.
            SmeIntegracaoError:
                Caso ocorra erro de comunicação, timeout, indisponibilidade
                do serviço ou qualquer falha retornada pela API do EOL.
            InternalError:
                Caso ocorra um erro interno ou de configuração da aplicação.
        """
        cls._valida_credenciais(login, senha)
        cls._valida_url()
        url = f"{SME_API_EOL_URL}{ENDPOINT_AUTENTICACAO}"
        headers = cls._obter_headers()
        data = json.dumps({"login": login, "senha": senha})

        try:
            logger.info("Iniciando autenticação no EOL. Login: %s", login)
            response = ApiEOLRepository.autentica_usuario(
                url=url,
                headers=headers,
                data=data,
            )
            response_data = cls._tratar_resposta(response, login)
            logger.info("Usuário autenticado com sucesso: %s", login)
            return response_data

        except requests.exceptions.Timeout:
            logger.error("Timeout na autenticação para login: %s", login)
            raise SmeIntegracaoError(
                "O serviço de autenticação demorou mais do que o esperado "
                "para responder. Tente novamente em alguns instantes."
            ) from None

        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão com EOL para login: %s", login)
            raise SmeIntegracaoError(
                "Não foi possível acessar o serviço de autenticação no "
                "momento. Tente novamente mais tarde."
            ) from None

        except requests.exceptions.RequestException as e:
            logger.exception(
                "Erro de comunicação com EOL para login %s: %s",
                login,
                str(e),
            )
            raise SmeIntegracaoError(
                "Ocorreu uma falha na comunicação com o serviço de "
                "autenticação"
            ) from None

        except (FalhaAutenticacaoError, SmeIntegracaoError):
            raise

        except Exception as err:
            logger.critical(
                "Erro inesperado na autenticação para login %s: %s",
                login,
                str(err),
                exc_info=True,
            )
            raise InternalError(
                "Ocorreu um erro interno durante a autenticação. Tente "
                "novamente em alguns instantes."
            ) from err

    @classmethod
    def usuario_existe_no_coresso(cls, login: str) -> bool:
        """
        Verifica se um usuário está cadastrado no CoreSSO.

        Realiza uma requisição à API de integração do CoreSSO para verificar
        se o usuário identificado pelo RF ou CPF informado já possui cadastro
        no sistema.

        Args:
            login (str):  login: RF (7 dígitos) ou CPF (11 dígitos) do usuário.

        Returns:
            bool: ``True`` se o usuário existir no CoreSSO (HTTP 200);
                caso contrário, retorna ``False``.
        """
        headers = {
            "accept": "text/plain",
            "x-api-eol-key": SME_API_EOL_TOKEN,
        }
        files = {
            "usuario": (None, login),
        }
        url = f"{SME_API_EOL_URL}{ENDPOINT_USUARIO_EXISTE_CORESSO}"
        response = ApiEOLRepository.usuario_existe(
            url, headers=headers, files=files
        )
        return response.status_code == 200

    @staticmethod
    def _valida_credenciais(login: object, senha: object) -> None:
        """
        Valida os dados de autenticação informados pelo usuário.

        Args:
            login (object): Login do usuário (RF ou CPF).
            senha (object): Senha do usuário.

        Raises:
            FalhaAutenticacaoError: Caso o login ou a senha não sejam
            informados ou possuam tipo diferente de ``str``.
        """
        if not login or not senha:
            raise FalhaAutenticacaoError(
                "Os campos login e senha são obrigatórios."
            )

        if not isinstance(login, str) or not isinstance(senha, str):
            raise FalhaAutenticacaoError(
                "As credenciais informadas são inválidas."
            )

    @staticmethod
    def _valida_url() -> None:
        """
        Valida se a  URL existe.

        Raises:
            InternalError:  Caso a URL base da integração não esteja
            configurada.
        """
        if not SME_API_EOL_URL:
            raise InternalError(
                "Serviço de autenticação não configurado. Entre em contato "
                "com o suporte."
            )

    @staticmethod
    def _obter_headers() -> dict[str, str]:
        """
        Obtém os cabeçalhos HTTP necessários para autenticação no EOL.

        Raises:
            InternalError: Caso o token de integração não esteja configurado.

        Returns:
            dict[str, str]: Cabeçalhos HTTP utilizados na requisição.
        """
        if not SME_API_EOL_TOKEN:
            raise InternalError(
                "Serviço de autenticação não configurado. Entre em contato "
                "com o suporte."
            )
        return {
            "accept": "application/json",
            "x-api-eol-key": SME_API_EOL_TOKEN,
            "Content-Type": "application/json-patch+json",
        }

    @staticmethod
    def _tratar_resposta(
        response: requests.Response, login: object
    ) -> dict[str, Any]:
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
            logger.warning("Credenciais inválidas para login: %s", login)
            raise FalhaAutenticacaoError(
                "Não foi possível autenticar o usuário. Verifique o login e "
                "a senha informados."
            )

        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            logger.warning("Rate limit atingido para login: %s", login)
            raise SmeIntegracaoError(
                "Foram realizadas muitas tentativas de autenticação. Aguarde "
                "alguns minutos antes de tentar novamente."
            )

        if not response.ok:
            logger.error(
                "Erro HTTP %s ao autenticar usuário %s. Resposta: %s",
                response.status_code,
                login,
                response.text[:200],
            )
            raise SmeIntegracaoError(
                "Não foi possível concluir a autenticação no momento."
            )

        try:
            response_data: dict[str, Any] = response.json()
        except ValueError as err:
            logger.exception(
                "Resposta inválida do EOL para login %s: %s",
                login,
                str(err),
            )
            raise SmeIntegracaoError(
                "O serviço de autenticação retornou uma resposta inválida."
            ) from err

        return response_data

    @classmethod
    def buscar_cargos(cls, registro_funcional: str) -> str:
        """Consulta cargos de um servidor na SME pelo RF.

        Args:
            registro_funcional (str): Registro funcional do servidor.

        Returns:
            str: Nome do cargo base do servidor.

        Raises:
            SmeIntegracaoError: Quando a consulta falha.
        """
        url = f"{SME_API_EOL_URL}/funcionarios/cargo/{registro_funcional}"
        headers = cls._obter_headers()
        response = ApiEOLRepository.get(url=url, headers=headers)

        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "Erro ao consultar cargos. Status: %s | Body: %s",
                response.status_code,
                response.text,
            )
            raise SmeIntegracaoError("Erro ao consultar cargos do servidor")

        dados: list = response.json()
        cargo: dict = (
            dados[0] if isinstance(dados, list) and len(dados) >= 1 else {}
        )
        nome_cargo: str = cargo.get("cargoBase", "Não informado")
        return nome_cargo

    @classmethod
    def dados_usuario(cls, registro_funcional: str) -> dict[str, str]:
        """Consulta dados de um servidor na SME pelo RF.

        Args:
            registro_funcional (str): Registro funcional do servidor.

        Returns:
            dict: Dados do usuário retornados pela API.

        Raises:
            SmeIntegracaoError: Quando a consulta falha.
        """
        url = (
            f"{SME_API_EOL_URL}/AutenticacaoCOMAPRE/{registro_funcional}/dados"
        )
        headers = cls._obter_headers()
        response = ApiEOLRepository.get(url=url, headers=headers)

        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "Erro ao consultar cargos. Status: %s | Body: %s",
                response.status_code,
                response.text,
            )
            raise SmeIntegracaoError("Erro ao consultar dados do servidor")
        informacoes: dict = response.json()
        return informacoes
