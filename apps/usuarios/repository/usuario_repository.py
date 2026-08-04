"""Repositorio do app usuarios."""

from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from apps.usuarios.constants import PerfilAcesso
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

    @classmethod
    def busca_usuario_existe_por_usermane(cls, username: str) -> dict:
        """Busca um usuário pelo nome de usuário.

        Recupera um usuário a partir do campo ``username`` e retorna seus
        dados em formato de dicionário..

        Args:
            username (str): RF ou CPF utilizado para localizar o usuário.

        Raises:
            ObjectDoesNotExist: Caso não exista um usuário com o ``username``
            informado.

        Returns:
            dict: Dicionário contendo os dados do usuário e suas informações
        de perfil de acesso.
        """
        try:
            usuario = Usuario.objects.get(username=username)
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
