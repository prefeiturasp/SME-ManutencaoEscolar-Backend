"""Model responsável pelo histórico do workflow."""

from django.conf import settings
from django.db import models


class HistoricoWorkflow(models.Model):
    """Registra as execuções e transições do workflow."""

    processo = models.ForeignKey(
        "core.ProcessoWorkflow",
        on_delete=models.PROTECT,
        related_name="historicos",
    )

    identificador = models.UUIDField()

    estado_anterior = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    acao = models.CharField(max_length=100)

    proximo_estado = models.CharField(max_length=100)

    terminal = models.BooleanField(default=False)

    sucesso = models.BooleanField(default=False)

    mensagem = models.TextField(blank=True)

    inicio = models.DateTimeField()

    fim = models.DateTimeField(null=True, blank=True)

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="historicos_workflow",
    )

    contexto = models.JSONField(default=dict)

    class Meta:
        ordering = ["-inicio"]

    def __str__(self) -> str:
        return f"{self.acao}: {self.estado_anterior} -> {self.proximo_estado}"
