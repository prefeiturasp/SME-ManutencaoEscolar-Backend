"""Model responsável pelo processo de workflow."""

import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ProcessoWorkflow(models.Model):
    """Representa o processo de workflow de uma entidade."""

    id_processo = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

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
        return f"{self.id_processo} - {self.estado_atual}"
