"""Service do app usuarios."""

import logging
from typing import Any

from django.core.exceptions import ObjectDoesNotExist

from apps.core.exceptions import EnvioEmailError
from apps.core.services.email_service import EmailService
from apps.usuarios.exceptions import (
    EmailUsuarioNaoEncontradoError,
    UsuarioNaoEncontradoError,
)
from apps.usuarios.repository.cargo_repository import CargoEOLRepository
from apps.usuarios.repository.usuario_repository import UsuarioRepository
from config import settings

logger = logging.getLogger(__name__)


class UsuarioService:
    """Service responsável pelas regras de negócio do usuário."""

    @classmethod
    def sincronizar_usuario(
        cls,
        dados_usuario: dict[str, Any],
        dados_cargo: dict[str, Any],
    ) -> dict[str, Any]:
        """Sincroniza um usuário retornado pelo EOL."""
        try:
            codigo_cargo = int(dados_cargo["codigo_cargo"])
            cargo = CargoEOLRepository.buscar_por_codigo(codigo_cargo)
        except (TypeError, ValueError):
            # Essa parte é temporária, para conseguir logar enquanto não temos
            # usuários com cargos
            cargo = CargoEOLRepository.buscar_por_codigo(3360)

        if cargo is None:
            raise ValueError("Cargo não encontrado")

        return UsuarioRepository.atualizar_ou_criar(
            dados_usuario=dados_usuario,
            codigo_cargo=str(cargo["codigo"]),
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
        token = UsuarioRepository.gerar_token_recuperar_senha(
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
