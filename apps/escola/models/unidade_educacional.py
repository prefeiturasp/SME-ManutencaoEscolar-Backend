"""_summary_."""

from django.db import models

from apps.core.models.mixins import UUIDMixin
from apps.escola.models import Diretor


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
        "escola.DiretoriaRegional",
        on_delete=models.PROTECT,
        related_name="escolas",
        help_text="Diretoria Regional de Educação da escola.",
    )
    tipo_escola = models.ForeignKey(
        "escola.TipoEscola",
        on_delete=models.PROTECT,
        related_name="escolas",
        help_text="Tipo da unidade escolar.",
    )
    subprefeitura = models.ForeignKey(
        "escola.Subprefeitura",
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

    @property
    def diretor_atual(self) -> Diretor | None:
        """Retorna o diretor atualmente vinculado à escola.

        A escola pode possuir vários registros históricos de diretores,
        mas apenas um vínculo pode estar ativo simultaneamente. O vínculo
        atual é identificado por `data_fim` igual a `None`.

        Returns:
            Diretor | None: O diretor atualmente vinculado à escola ou
                `None` quando a escola não possui diretor atual.
        """
        historico = (
            self.historico_diretores.filter(data_fim__isnull=True)
            .select_related("diretor")
            .first()
        )
        return historico.diretor if historico else None
