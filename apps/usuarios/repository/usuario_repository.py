"""Repositorio do app usuarios."""

from typing import Any

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from apps.core.exceptions import (
    TokenInvalidoError,
)
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.exceptions import (
    UsuarioNaoEncontradoError,
)
from apps.usuarios.models import CargoEOL, Usuario


class UsuarioRepository:
    """Repository responsável pela persistência de usuários."""

    @classmethod
    @transaction.atomic
    def atualizar_ou_criar(
        cls,
        dados_usuario: dict[str, Any],
        codigo_cargo: str,
    ) -> dict[str, Any]:
        """Atualiza ou cria um usuário utilizando RF ou CPF."""
        filtros: dict[str, Any] = {}
        nome = dados_usuario["nome"]
        email = dados_usuario["email"]
        registro_funcional = dados_usuario["codigo_rf"]
        cpf = dados_usuario["cpf"]
        username = registro_funcional or cpf
        if username is None:
            raise ValueError("É necessário fornecer registro_funcional ou cpf")

        if registro_funcional and len(registro_funcional) == 7:
            filtros["registro_funcional"] = registro_funcional
        else:
            filtros["cpf"] = registro_funcional or cpf

        cargo = CargoEOL.objects.get(codigo=codigo_cargo)
        usuario, criado = Usuario.objects.get_or_create(
            defaults={
                "nome": nome,
                "email": email,
                "cargo": cargo,
                "username": username,
            },
            **filtros,
        )

        if not criado:
            usuario.nome = nome
            usuario.email = email
            usuario.cargo = cargo

            usuario.save(
                update_fields=[
                    "nome",
                    "email",
                    "cargo",
                ]
            )

        return cls._retorna_usuario_em_dicionario(usuario)

    @staticmethod
    def usuario_existe_por_id(usuario_id: int) -> bool:
        """Verifica se existe um usuário ativo com o identificador informado.

        Args:
            usuario_id (int): Identificador único do usuário.

        Returns:
            bool: ``True`` se existir um usuário ativo com o identificador
            informado; caso contrário, ``False``.
        """
        return Usuario.objects.filter(
            id=usuario_id,
            is_active=True,
        ).exists()

    @staticmethod
    def retorna_username_usuario(usuario_id: int) -> dict[str, str]:
        """Retorna o username de um usuário ativo.

        Args:
            usuario_id (int): Identificador único do usuário.

        Returns:
            dict[str, str]: Dicionário contendo o username do usuário.

        Raises:
            UsuarioNaoEncontradoError: Se não existir um usuário ativo com o
                identificador informado.
        """
        username = (
            Usuario.objects.filter(
                id=usuario_id,
                is_active=True,
            )
            .values_list("username", flat=True)
            .first()
        )

        if username is None:
            raise UsuarioNaoEncontradoError(
                title="Usuário não encontrado.",
                detail="Não foi encontrado um usuário ativo com o "
                "identificador informado.",
            )

        return {"username": username}

    @classmethod
    def _consulta_por_username(cls, username: str) -> Usuario:
        """Recupera um usuário pelo username.

        Args:
            username (str): Username do usuário (RF ou CPF).

        Raises:
            ObjectDoesNotExist: Caso não exista um usuário com o username
                informado.

        Returns:
            Usuario: Instância do usuário encontrado.
        """
        try:
            return Usuario.objects.get(username=username)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist from None

    @classmethod
    def busca_usuario_por_username(cls, username: str) -> dict:
        """Busca um usuário pelo nome de usuário.

        Recupera um usuário a partir do campo ``username`` e e retorna seus
        dados em formato de dicionário.

        Args:
            username (str): Username de usuário (RF ou CPF) utilizado para
                localizar.
        Raises:
            ObjectDoesNotExist: Caso não exista um usuário com o ``username``
            informado.

        Returns:
            dict: Dados do usuário e suas informações de perfil de acesso.
        """
        try:
            usuario = cls._consulta_por_username(username)
            return cls._retorna_usuario_em_dicionario(usuario)

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist from None

    @staticmethod
    def _retorna_usuario_em_dicionario(usuario: Usuario) -> dict:
        """Transforma um objeto ``Usuario`` para um dicionário.

        Args:
            usuario (Usuario): Instância do usuário a ser convertida.

        Returns:
            dict: Dicionário contendo os seguintes dados:

            - ``id``: Identificador do usuário.
            - ``uuid``: UUID do usuário.
            - ``nome``: Nome completo.
            - ``email``: Endereço de e-mail.
            - ``registro_funcional``: Registro funcional.
            - ``cpf``: CPF do usuário.
            - ``username``: Nome de usuário.
            - ``perfil_acesso``: Informações do cargo e perfil de acesso.
        """
        return {
            "id": usuario.id,
            "uuid": usuario.uuid,
            "nome": usuario.nome,
            "email": usuario.email,
            "registro_funcional": usuario.registro_funcional,
            "cpf": usuario.cpf,
            "username": usuario.username,
            "perfil_acesso": {
                "cargo": usuario.cargo.nome,
                "perfil": {
                    "codigo": usuario.perfil,
                    "descricao": PerfilAcesso(usuario.perfil).label,
                },
            },
        }

    @classmethod
    def gerar_token_recuperar_senha(cls, username: str) -> dict:
        """Gera um token para recuperação de senha do usuário.

        Busca o usuário pelo nome de usuário e gera um token de recuperação
        de senha utilizando o ``PasswordResetTokenGenerator`` do Django.

        Args:
            username (str):  Nome de usuário utilizado para localizar o
                usuário que terá o token de recuperação gerado.


        Returns:
            dict: Dicionário contendo o token de recuperação na chave
                ``token_recuperacao``.
        """
        usuario = cls._consulta_por_username(username)
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(usuario)
        return {"token_recuperacao": token}

    @classmethod
    def verificar_token_atualizar_senha(
        cls,
        username: str,
        token: str,
    ) -> None:
        """Altera a senha de um usuário a partir de token de recuperação.

        Args:
            username (str): Nome de usuário (RF ou CPF) do usuário.
            token (str): Token de recuperação de senha enviado por e-mail.

        Raises:
            TokenInvalidoError: Se o token for inválido ou expirado.
        """
        usuario = cls._consulta_por_username(username)
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(usuario, token):
            raise TokenInvalidoError(
                title="Token inválido.",
                detail=(
                    "O token de recuperação de senha é inválido ou expirou."
                ),
            )

    @classmethod
    def invalidar_token_recuperacao_senha(
        cls, username: str, senha: str
    ) -> None:
        """Invalida o token de recuperação de senha do usuário.

        Atualiza a senha do usuário utilizando o mecanismo de hash do Django.
        A alteração do campo `password` faz com que tokens de recuperação
        previamente gerados pelo `PasswordResetTokenGenerator` deixem de ser
        válidos.

        Args:
            username (str): Nome de usuário utilizado para localizar o usuário.
            senha (str): Nova senha que será definida para o usuário.
        """
        usuario = cls._consulta_por_username(username)
        usuario.set_password(senha)
        usuario.save(update_fields=["password"])
