"""Modelo referentes aos usuarios do sistema."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models

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
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self) -> str:
        return self.nome

    @property
    def perfil(self) -> str:
        """Retorna o perfil de acesso através do cargo."""
        return self.cargo.perfil
