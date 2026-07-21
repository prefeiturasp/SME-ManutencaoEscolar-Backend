"""_summary_."""

from typing import Any

from django.db import transaction

from apps.usuarios.models import CargoEOL, Usuario


class UsuarioRepository:
    """Repository responsável pela persistência de usuários."""

    @classmethod
    @transaction.atomic
    def atualizar_ou_criar(
        cls,
        *,
        nome: str,
        email: str,
        registro_funcional: str | None,
        cpf: str | None,
        cargo: CargoEOL,
    ) -> dict[str, Any]:
        """Atualiza ou cria um usuário utilizando RF ou CPF."""
        filtros: dict[str, Any] = {}
        username = registro_funcional or cpf
        if username is None:
            raise ValueError("É necessário fornecer registro_funcional ou cpf")

        if registro_funcional:
            filtros["registro_funcional"] = registro_funcional
        else:
            filtros["cpf"] = cpf

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
            "cargo_id": usuario.cargo_id,
        }
        return dict_usuario
