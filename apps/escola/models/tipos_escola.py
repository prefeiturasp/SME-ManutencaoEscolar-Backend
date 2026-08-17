"""Modelos relacionados aos tipos de escola."""

from django.db import models

from apps.core.models.mixins import TimestampMixin, UUIDMixin


class TipoEscola(UUIDMixin, TimestampMixin):
    """Representa o tipo de unidade escolar cadastrado no sistema EOL."""

    codigo_eol = models.PositiveIntegerField(
        unique=True,
        help_text="Código identificador do tipo de escola no sistema EOL.",
    )
    sigla = models.CharField(
        max_length=50,
        unique=True,
        help_text="Sigla que identifica o tipo de escolar.",
    )
    data_atualizacao_eol = models.DateTimeField(
        help_text="Data e hora da última atualização do registro no sistema "
        "EOL.",
    )

    class Meta:
        ordering = ("sigla",)
        verbose_name = "Tipo de unidade"
        verbose_name_plural = "Tipos de unidade"

    def __str__(self) -> str:
        return f"{self.codigo_eol} - {self.sigla}"
