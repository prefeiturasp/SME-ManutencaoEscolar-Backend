"""Modelos da aplicação Serviço."""

from django.db import models
from django.db.models.functions import Lower

from apps.core.models.mixins import BaseModel


class Servico(BaseModel):
    """Representa o cadastro de um serviço."""

    nome = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["-status", "-id"]
        indexes = [models.Index(fields=["status"])]
        constraints=[
            models.UniqueConstraint(
                Lower("nome"),
                condition=models.Q(deletado_em__isnull=True),
                name="servico_nome_unico_case_insensitive",
            ),
        ]
        

    def __str__(self) -> str:
        return self.nome
