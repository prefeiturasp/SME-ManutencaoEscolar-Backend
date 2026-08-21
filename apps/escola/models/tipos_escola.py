"""Modelos relacionados aos tipos de escola."""

from django.db import models

from apps.core.models.mixins import UUIDMixin
from apps.escola.constants import TIPO_ESCOLA_NAO_ACEITAS


class TipoEscolaQuerySet(models.QuerySet):
    """QuerySet customizado para tipos de escola."""

    def aceitos(self) -> "TipoEscolaQuerySet":
        """Retorna apenas os tipos de escola aceitos pelo sistema."""
        return self.exclude(sigla__in=TIPO_ESCOLA_NAO_ACEITAS)


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

    objects = TipoEscolaQuerySet.as_manager()

    class Meta:
        ordering = ("sigla",)
        verbose_name = "Tipo de unidade"
        verbose_name_plural = "Tipos de unidade"

    def __str__(self) -> str:
        return f"{self.codigo_eol} - {self.sigla}"
