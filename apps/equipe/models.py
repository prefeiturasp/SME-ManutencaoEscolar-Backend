"""Modelos do domínio Equipe."""

from django.db import models
from django.db.models.functions import Lower

from apps.core.models.mixins import BaseModel
from apps.empresa.models import Empresa
from apps.equipe.constants import EquipeErrorMessages
from apps.lote.models import Lote
from apps.profissional.models import FuncaoProfissional, Profissional


class Equipe(BaseModel):
    """Representa uma equipe de profissionais de uma empresa e lote."""

    nome = models.CharField(max_length=255)
    situacao = models.BooleanField(default=True)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="equipes",
    )
    lote = models.ForeignKey(
        Lote,
        on_delete=models.PROTECT,
        related_name="equipes",
    )

    class Meta:
        """Configura os metadados de equipe."""

        verbose_name = "Equipe"
        verbose_name_plural = "Equipes"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                Lower("nome"),
                "empresa",
                condition=models.Q(deletado_em__isnull=True),
                name="equipe_nome_empresa_unico",
                violation_error_message=(
                    EquipeErrorMessages.NOME_EQUIPE_DUPLICADO
                ),
            )
        ]

    def __str__(self) -> str:
        """Retorna o nome da equipe."""
        return self.nome


class ProfissionalEquipe(BaseModel):
    """Representa o vínculo de um profissional e sua função na equipe."""

    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.CASCADE,
        related_name="profissionais",
    )
    profissional = models.ForeignKey(
        Profissional,
        on_delete=models.PROTECT,
        related_name="vinculos_equipe",
    )
    funcao = models.ForeignKey(
        FuncaoProfissional,
        on_delete=models.PROTECT,
        related_name="vinculos_equipe",
    )

    class Meta:
        """Configura os metadados do vínculo com a equipe."""

        verbose_name = "Profissional da equipe"
        verbose_name_plural = "Profissionais da equipe"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["equipe", "profissional"],
                condition=models.Q(deletado_em__isnull=True),
                name="profissional_unico_por_equipe",
                violation_error_message=(
                    EquipeErrorMessages.PROFISSIONAL_DUPLICADO
                ),
            )
        ]

    def __str__(self) -> str:
        """Retorna profissional e equipe do vínculo."""
        return f"{self.profissional} - {self.equipe}"
