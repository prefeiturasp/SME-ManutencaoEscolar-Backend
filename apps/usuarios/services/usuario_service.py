"""Service do app usuarios."""

import logging
from typing import Any

from django.core.exceptions import ObjectDoesNotExist

from apps.core.services.email_service import EmailService
from apps.usuarios.exceptions import UsuarioNaoEncontradoError
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
            usuario = UsuarioRepository.busca_usuario_por_usermane(rf_ou_cpf)
            return usuario
        except ObjectDoesNotExist:
            raise UsuarioNaoEncontradoError(
                title="Usuário não encontrado.",
                detail="Usuário não está na base de dados ou está inativado",
            ) from None

    @staticmethod
    def enviar_email_recuperacao_senha(usuario: dict) -> None:
        """Envia um e-mail de recuperação de senha para o usuário.

        Gera um token de recuperação de senha, monta o link para redefinição
        de senha, renderiza o template HTML e envia o e-mail para o endereço
        cadastrado do usuário.

        Args:
            usuario (dict):  Dicionário contendo os dados do usuário. Deve
                possuir, no mínimo, as chaves ``nome``, ``email`` e
                ``username``.
        """
        token = UsuarioRepository.gerar_token_recuperar_senha(
            usuario["username"]
        )

        link = (
            f"{settings.FRONTEND_URL}/recuperar-senha/"
            f"{token['token_recuperacao']}"
        )

        contexto = {
            "nome": usuario["nome"],
            "url": link,
            "username": usuario["username"],
        }

        EmailService.enviar(
            assunto="Recuperação de senha",
            template="usuarios/recuperar_senha.html",
            contexto=contexto,
            destinatarios=[usuario["email"]],
        )
