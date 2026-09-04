"""Modelos relacionados ao cadastro de lotes."""

from django.db import models
from django.db.models import QuerySet

from apps.core.models.mixins import BaseModel
from apps.escola.models.diretoria_regional import DiretoriaRegional


class Lote(BaseModel):
    """Representa um lote vinculado a uma empresa."""

    codigo_cadastro = models.CharField(
        verbose_name="código de cadastro",
        max_length=255,
    )
    nome = models.CharField(
        verbose_name="nome",
        max_length=255,
    )
    status = models.BooleanField(
        verbose_name="status",
        default=True,
    )
    empresa = models.ForeignKey(
        "empresa.Empresa",
        verbose_name="empresa",
        on_delete=models.PROTECT,
        related_name="lotes",
    )
    periodo_inicial = models.DateField(
        verbose_name="periodo inicial",
        null=True,
        blank=True,
    )
    periodo_final = models.DateField(
        verbose_name="periodo final",
        null=True,
        blank=True,
    )

    class Meta:
        """Configura os metadados do modelo."""

        verbose_name = "lote"
        verbose_name_plural = "lotes"
        ordering = ["-status", "-id"]

    def __str__(self) -> str:
        """Retorna a representação textual do lote."""
        return self.nome

    @property
    def diretorias_regionais(self) -> QuerySet[DiretoriaRegional]:
        """Retorna todas as Diretorias Regionais vinculadas ao lote."""
        return DiretoriaRegional.objects.filter(vinculo_lote__lote=self)


class LoteDiretoriaRegional(BaseModel):
    """Representa o vínculo exclusivo entre Diretoria Regional e lote."""

    lote = models.ForeignKey(
        Lote,
        verbose_name="lote",
        on_delete=models.CASCADE,
        related_name="vinculos_diretoria_regional",
    )
    diretoria_regional = models.ForeignKey(
        "escola.DiretoriaRegional",
        verbose_name="Diretoria Regional",
        on_delete=models.PROTECT,
        related_name="vinculo_lote",
    )

    class Meta:
        """Configura os metadados do vínculo lote e Diretoria Regional."""

        verbose_name = "Diretoria Regional do lote"
        verbose_name_plural = "Diretorias Regionais do lote"
        ordering = ["id"]

    def __str__(self) -> str:
        """Retorna a represenptação textual do vínculo."""
        return f"{self.lote} - {self.diretoria_regional}"
