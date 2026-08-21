"""_summary_."""

from django.db import models

from apps.core.models.mixins import UUIDMixin
from apps.escola.models.diretoria_regional import DiretoriaRegional
from apps.escola.models.subprefeitura import Subprefeitura
from apps.escola.models.tipos_escola import TipoEscola


class Unidadeeducacional(UUIDMixin):
    """Representa uma unidade escolar cadastrada no sistema EOL."""

    codigo_eol = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código identificador da escola no sistema EOL.",
    )
    nome = models.CharField(
        max_length=255,
        help_text="Nome da escola.",
    )
    diretoria_regional = models.ForeignKey(
        DiretoriaRegional,
        on_delete=models.PROTECT,
        related_name="escolas",
        help_text="Diretoria Regional de Educação da escola.",
    )
    tipo_escola = models.ForeignKey(
        TipoEscola,
        on_delete=models.PROTECT,
        related_name="escolas",
        help_text="Tipo da unidade escolar.",
    )
    subprefeitura = models.ForeignKey(
        Subprefeitura,
        on_delete=models.PROTECT,
        related_name="escolas",
        help_text="Subprefeitura onde a escola está localizada.",
    )
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ("nome",)
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"

    def __str__(self) -> str:
        return f"{self.codigo_eol} - {self.nome}"
