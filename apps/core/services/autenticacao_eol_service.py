"""Serviços responsáveis pela autenticação de usuários no EOL."""

import json
import logging
from typing import Any

import requests

from apps.core.constants import (
    ENDPOINT_ALTERAR_SENHA_CORESSO,
    ENDPOINT_AUTENTICACAO,
    ENDPOINT_USUARIO_EXISTE_CORESSO,
)
from apps.core.exceptions import (
    FalhaAutenticacaoError,
    InternalError,
    SmeIntegracaoError,
)
from apps.core.repository.autenticacao_eol_repository import ApiEOLRepository
from apps.core.repository.token_repository import TokenRepository
from apps.core.services.token_service import TokenService
from apps.usuarios.services.usuario_service import UsuarioService
from config.settings import SME_API_EOL_TOKEN, SME_API_EOL_URL

logger = logging.getLogger(__name__)
DADO_NAO_INFORMADO = "Não informado"


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
            logger.info("Usuário autenticado com sucesso: %s", login)
            return response

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

    @classmethod
    def buscar_cargos(cls, registro_funcional: str) -> dict:
        """Consulta cargos de um servidor na SME pelo RF.

        Args:
            registro_funcional (str): Registro funcional do servidor.

        Returns:
            dict: Nome  e código do cargo base do servidor.

        Raises:
            SmeIntegracaoError: Quando a consulta falha.
        """
        url = f"{SME_API_EOL_URL}/funcionarios/cargo/{registro_funcional}"
        headers = cls._obter_headers()
        try:
            response = ApiEOLRepository.buscar_cargos(url=url, headers=headers)
        except SmeIntegracaoError:
            logging.exception(
                "Erro ao consultar cargos",
            )
            raise

        # No futuro, se retornar lista vazia, retorna FalhaAutenticacaoError
        cargo: dict = (
            response[0]
            if isinstance(response, list) and len(response) >= 1
            else {}
        )
        informacoes_cargo: dict = {
            "nome_cargo": cargo.get("cargoBase", DADO_NAO_INFORMADO),
            "codigo_cargo": cargo.get("cdCargoBase", DADO_NAO_INFORMADO),
        }
        return informacoes_cargo

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
        try:
            response = ApiEOLRepository.obter_dados_usuarios(
                url=url, headers=headers
            )
        except SmeIntegracaoError:
            logging.exception(
                "Erro ao consultar dados do servidor",
            )
            raise

        return response

    @classmethod
    def login(cls, login: object, senha: object) -> dict[str, Any]:
        dados_autenticacao = cls.autentica(
            login=login,
            senha=senha,
        )
        codigo_rf = dados_autenticacao["codigoRf"]
        informaoes_cargo = cls.buscar_cargos(registro_funcional=codigo_rf)
        dados_usuario = cls.dados_usuario(codigo_rf)
        dados_usuario["codigo_rf"] = codigo_rf
        usuario = UsuarioService.sincronizar_usuario(
            dados_usuario=dados_usuario,
            dados_cargo=informaoes_cargo,
        )
        token = TokenService.gerar_tokens(usuario["id"])
        return {
            "refresh": token["refresh"],
            "access": token["access"],
            "usuario": {
                **usuario,
                "diretoria_regional": dados_usuario.get(
                    "dre", DADO_NAO_INFORMADO
                ),
                "unidade_educacional": dados_usuario.get(
                    "nomeUe", DADO_NAO_INFORMADO
                ),
            },
        }

    @classmethod
    def alterar_senha_no_coresso(cls, login: str, nova_senha: str) -> None:
        """Altera a senha do usuário e invalida o token de recuperação.

        Monta os dados necessários para a requisição à API do CoreSSO e
        delega a alteração da senha ao repositório de integração. Após uma
        alteração bem-sucedida, invalida o token de recuperação de senha
        associado ao usuário.

        Args:
            login (str): Login do usuário cuja senha será alterada
            nova_senha (str): Nova senha que será definida para o usuário.

        Raises:
            FalhaAutenticacaoError: Levantada quando ocorre uma falha de
                autenticação durante a alteração da senha no CoreSSO.
            SmeIntegracaoError: Levantada quando ocorre uma falha na
                comunicação ou no processamento da requisição pela API de
                integração do SME.
        """
        headers = {
            "accept": "text/plain",
            "x-api-eol-key": SME_API_EOL_TOKEN,
        }
        files = {
            "Usuario": (None, login),
            "Senha": (None, nova_senha),
        }
        url = f"{SME_API_EOL_URL}{ENDPOINT_ALTERAR_SENHA_CORESSO}"
        try:
            ApiEOLRepository.alterar_senha(url, headers=headers, files=files)
            TokenRepository.atualizar_senha_usuario(login, nova_senha)
        except FalhaAutenticacaoError as exc:
            raise FalhaAutenticacaoError(exc) from exc
        except SmeIntegracaoError as exc:
            raise SmeIntegracaoError(exc) from exc
