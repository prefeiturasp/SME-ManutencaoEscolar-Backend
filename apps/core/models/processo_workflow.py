"""Model responsável pelo processo de workflow."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models.mixins import UUIDMixin


class ProcessoWorkflow(UUIDMixin):
    """Representa o processo de workflow de uma entidade."""

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="processos_workflow",
    )

    entidade_referencia = models.CharField(max_length=255)

    entidade = GenericForeignKey(
        "content_type",
        "entidade_referencia",
    )

    estado_atual = models.CharField(max_length=100)

    terminal = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "entidade_referencia"],
                name="unique_entidade_processo_workflow",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.uuid} - {self.estado_atual}"
