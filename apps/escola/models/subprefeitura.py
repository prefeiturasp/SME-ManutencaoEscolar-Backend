"""Modelos relacionados as Subprefeituras."""

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
    diretoria_regional = models.ForeignKey(
        "escola.DiretoriaRegional",
        verbose_name="Diretoria Regional",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subprefeituras",
        help_text="Diretoria Regional responsável pela Subprefeitura.",
    )

    class Meta:
        ordering = ("nome",)
        verbose_name = "Subprefeitura"
        verbose_name_plural = "Subprefeituras"

    def __str__(self) -> str:
        return f"{self.codigo_eol} - {self.nome}"
