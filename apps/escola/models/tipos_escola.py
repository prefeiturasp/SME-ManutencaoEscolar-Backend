"""Modelos relacionados aos tipos de escola."""

from django.db import models

from apps.core.models.mixins import UUIDMixin


class TipoEscola(UUIDMixin):
    """Representa o tipo de unidade escolar cadastrado no sistema EOL."""

    codigo_eol = models.PositiveIntegerField(
        unique=True,
        help_text="Código identificador do tipo de escola no sistema EOL.",
    )
    sigla = models.CharField(
        max_length=50,
        help_text="Sigla que identifica o tipo de escolar.",
    )

    class Meta:
        ordering = ("sigla",)
        verbose_name = "Tipo de unidade"
        verbose_name_plural = "Tipos de unidade"

    def __str__(self) -> str:
        return f"{self.codigo_eol} - {self.sigla}"
