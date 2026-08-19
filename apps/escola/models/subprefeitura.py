"""_summary_."""

from django.db import models

from apps.core.models.mixins import UUIDMixin


class Subprefeitura(UUIDMixin):
    """Representa uma Subprefeitura cadastrada no sistema EOL."""

    codigo_eol = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código identificador da Subprefeitura no sistema EOL.",
    )
    nome = models.CharField(
        max_length=255,
        help_text="Nome da Subprefeitura.",
    )

    class Meta:
        ordering = ("nome",)
        verbose_name = "Subprefeitura"
        verbose_name_plural = "Subprefeituras"

    def __str__(self) -> str:
        return f"{self.codigo_eol} - {self.nome}"
