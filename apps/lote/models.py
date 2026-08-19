"""Modelos relacionados ao cadastro de lotes."""

from django.db import models
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
        ordering = ["nome"]

    def __str__(self) -> str:
        """Retorna a representação textual do lote."""
        return self.nome

    @property
    def dres(self):
        """Retorna todas as DREs vinculadas ao lote."""
        return DiretoriaRegional.objects.filter(
            vinculo_lote__lote=self
        )

class LoteDRE(BaseModel):
    """Representa o vínculo exclusivo entre uma DRE e um lote."""

    lote = models.ForeignKey(
        Lote,
        verbose_name="lote",
        on_delete=models.CASCADE,
        related_name="vinculos_dre",
    )
    dre = models.OneToOneField(
        "escola.DiretoriaRegional",
        verbose_name="DRE",
        on_delete=models.PROTECT,
        related_name="vinculo_lote",
    )

    class Meta:
        """Configura os metadados do vínculo entre lote e DRE."""

        verbose_name = "DRE do lote"
        verbose_name_plural = "DREs dos lotes"
        ordering = ["id"]

    def __str__(self) -> str:
        """Retorna a represenptação textual do vínculo."""
        return f"{self.lote} - {self.dre}"
