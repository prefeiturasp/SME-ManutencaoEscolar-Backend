"""Service do app usuarios."""

import logging
from typing import Any

from django.core.exceptions import ObjectDoesNotExist

from apps.core.exceptions import (
    EnvioEmailError,
)
from apps.core.repository.token_repository import TokenRepository
from apps.core.services.email_service import EmailService
from apps.escola.repository.responsavel_unidade_repository import (
    ResponsavelUnidadeRepository,
)
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.exceptions import (
    EmailUsuarioNaoEncontradoError,
    UsuarioNaoEncontradoError,
)
from apps.usuarios.repository.usuario_repository import UsuarioRepository
from config import settings

logger = logging.getLogger(__name__)


class UsuarioService:
    """Service responsável pelas regras de negócio do usuário."""

    @classmethod
    def sincronizar_usuario(
        cls,
        dados_usuario: dict[str, Any],
    ) -> dict[str, Any]:
        """Sincroniza um usuário retornado pelo EOL.

        Args:
            dados_usuario (dict[str, Any]): Dicionário contendo os dados
                do usuário obtidos durante o processo de autenticação.

        Returns:
            dict[str, Any]: Dicionário com os dados do usuário retornados
            pelo repositório após a sincronização.
        """
        return UsuarioRepository.atualizar_ou_criar(
            dados_usuario=dados_usuario
        )

    @classmethod
    def obter_usuario_por_rf_cpf(cls, rf_ou_cpf: str) -> dict:
        """Obtenha um usuário pelo registro funcional ou CPF.

        Busca um usuário utilizando o registro funcional ou CPF informado
        (armazenado no campo ``username``) e retorna seus dados em formato
        de dicionário.

        Args:
            rf_ou_cpf (str): Registro funcional ou CPF do usuário.

        Raises:
            UsuarioNaoEncontradoError: Caso não exista um usuário ativo
                correspondente ao registro funcional ou CPF informado.


        Returns:
            dict: Dicionário contendo os dados do usuário e suas informações
            de perfil de acesso.
        """
        try:
            usuario = UsuarioRepository.busca_usuario_por_username(rf_ou_cpf)
            if usuario["email"] is None or not usuario["email"].strip():
                raise EmailUsuarioNaoEncontradoError(
                    title="E-mail não encontrado.",
                    detail="Não foi encontrado e-mail para esse RF ou CPF.",
                )
            return usuario
        except ObjectDoesNotExist:
            raise UsuarioNaoEncontradoError(
                title="Usuário não encontrado.",
                detail="Verifique se o RF ou CPF digitados estão corretos e "
                "tente novamente",
            ) from None

    @classmethod
    def obter_usuario_autenticado(cls, rf_ou_cpf: str) -> dict[str, Any]:
        """Obtém os dados do usuário autenticado para o endpoint ``/me``.

        Complementa os dados do usuário com a unidade educacional e a
        diretoria regional, conforme o perfil de acesso:

        - ``UE``: dados completos da unidade educacional e nome da DRE;
        - ``DRE``: nome da diretoria regional, sem unidade educacional;
        - ``SME`` e ``EMPRESA`` (ou sem perfil): ambos ``None``.

        Args:
            rf_ou_cpf (str): Registro funcional ou CPF do usuário.

        Returns:
            dict[str, Any]: Dados do usuário acrescidos de
            ``unidade_educacional`` e ``diretoria_regional``.

        Raises:
            UsuarioNaoEncontradoError: Se o usuário não for encontrado.
            EmailUsuarioNaoEncontradoError: Se o usuário não tiver e-mail.
        """
        usuario = cls.obter_usuario_por_rf_cpf(rf_ou_cpf)
        perfil = usuario["perfil_acesso"].get("perfil", {}).get("codigo")

        vinculo: dict[str, Any] = {
            "unidade_educacional": None,
            "diretoria_regional": None,
        }
        if perfil == PerfilAcesso.UE:
            vinculo = cls._vinculo_unidade_educacional(usuario["username"])
        elif perfil == PerfilAcesso.DRE:
            vinculo["diretoria_regional"] = cls._obter_dre_do_usuario(
                usuario["username"]
            )
        return {**usuario, **vinculo}

    @staticmethod
    def _vinculo_unidade_educacional(username: str) -> dict[str, Any]:
        """Retorna a unidade educacional e o nome da DRE do diretor."""
        informacoes = (
            ResponsavelUnidadeRepository.buscar_unidade_educacional_ativa(
                username
            )
        )
        if informacoes is None:
            return {"unidade_educacional": None, "diretoria_regional": None}
        return {
            "unidade_educacional": informacoes["unidade_educacional"],
            "diretoria_regional": informacoes["diretoria_regional"],
        }

    @staticmethod
    def _obter_dre_do_usuario(username: str) -> str | None:
        """Retorna o nome da DRE do usuário com perfil DRE.

        Ainda não há vínculo entre o usuário com perfil DRE e a diretoria
        regional (definição pendente), por isso retorna ``None``.
        """
        return None

    @staticmethod
    def enviar_email_recuperacao_senha(usuario: dict) -> None:
        """Envia um e-mail de recuperação de senha para o usuário.

        Gera um token de recuperação de senha, monta o link para
        redefinição de senha e solicita o envio assíncrono de um e-mail
        HTML contendo as instruções de recuperação para o endereço
        cadastrado do usuário.

        Args:
            usuario (dict):  Dicionário contendo os dados do usuário. Deve
                possuir, no mínimo, as chaves ``nome``, ``email`` e
                ``username``.
        Raises:
            EnvioEmailError: Caso ocorra uma falha ao solicitar o envio do
                e-mail de recuperação de senha.
        """
        token = TokenRepository.gerar_token_recuperar_senha(
            usuario["username"]
        )

        link = (
            f"{settings.FRONTEND_URL}/redefinir-senha/?id="
            f"{usuario['username']}&token={token['token_recuperacao']}"
        )

        contexto = {
            "nome": usuario["nome"],
            "url": link,
            "username": usuario["username"],
        }
        try:
            EmailService.enviar(
                assunto="Recuperação de senha",
                template="recuperar_senha.html",
                contexto=contexto,
                destinatarios=[usuario["email"]],
            )
        except Exception:
            logger.exception(
                "Erro ao enviar e-mail para o usuário '%s'.",
                usuario["username"],
            )
            raise EnvioEmailError(
                title="Erro ao enviar e-mail.",
                detail="Parece que estamos com uma instabilidade no momento. "
                "Tente novamnete daqui a pouco",
            ) from None
