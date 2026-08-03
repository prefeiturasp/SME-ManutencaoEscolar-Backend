"""Repositorio do app usuarios."""

from typing import Any

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

        dict_usuario = {
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
        return dict_usuario

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
