"""Modelos do domínio Equipe."""

from django.core.exceptions import ValidationError
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
        ordering = ["-situacao", "-id"]
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

    def clean(self) -> None:
        """Valida se a empresa informada está associada ao lote."""
        super().clean()
        if (
            self.empresa_id
            and self.lote_id
            and self.empresa_id != self.lote.empresa_id
        ):
            raise ValidationError(
                {"empresa": EquipeErrorMessages.EMPRESA_LOTE_INVALIDA}
            )


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

    def clean(self) -> None:
        """Valida se a função informada pertence ao profissional."""
        super().clean()
        if (
            self.profissional_id
            and self.funcao_id
            and self.profissional_id != self.funcao.profissional_id
        ):
            raise ValidationError(
                {"funcao": EquipeErrorMessages.FUNCAO_INVALIDA}
            )
