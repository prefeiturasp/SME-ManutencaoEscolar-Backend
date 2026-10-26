"""Modelo referentes aos usuarios do sistema."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models

from apps.usuarios.constants import FUNCIONALIDADES_POR_PERFIL
from apps.usuarios.models.cargo_eol import CargoEOL


class Usuario(AbstractUser):
    """Modelo responsável por representar os usuários do sistema."""

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, null=True
    )
    nome = models.CharField("Nome", max_length=255)
    registro_funcional = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        unique=True,
        validators=[MinLengthValidator(7)],
    )
    cpf = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        unique=True,
        validators=[MinLengthValidator(11)],
    )
    cargo = models.ForeignKey(
        CargoEOL,
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self) -> str:
        return self.nome

    @property
    def perfil(self) -> str | None:
        """Retorna o perfil de acesso através do cargo."""
        if self.cargo is None:
            return None
        return self.cargo.perfil or None

    @property
    def funcionalidades(self) -> list[str]:
        """Retorna as funcionalidades liberadas para o perfil do usuário.

        Usuários sem cargo, ou com cargo sem perfil de acesso, não têm
        nenhuma funcionalidade liberada.
        """
        liberadas: frozenset[str] = FUNCIONALIDADES_POR_PERFIL.get(
            self.perfil or "", frozenset()
        )
        return sorted(str(funcionalidade) for funcionalidade in liberadas)

    def tem_acesso(self, funcionalidade: str) -> bool:
        """Indica se o perfil do usuário permite usar a funcionalidade."""
        return funcionalidade in self.funcionalidades
