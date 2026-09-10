"""Modelos da aplicação Cargo."""

from django.db import models
from django.db.models.functions import Lower

from apps.core.models.mixins import BaseModel


class Cargo(BaseModel):
    """Representa o cadastro de um cargo."""

    nome = models.CharField(max_length=255)
    exige_documento = models.BooleanField(default=False)
    status = models.BooleanField(default=True)

    class Meta:
        """Configurações do modelo Cargo."""

        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ["-status", "-id"]
        constraints = [
            models.UniqueConstraint(
                Lower("nome"),
                condition=models.Q(deletado_em__isnull=True),
                name="cargo_nome_unico_case_insensitive",
            ),
        ]

    def __str__(self) -> str:
        """Retorna o nome do cargo."""
        return self.nome


class DocumentoCargo(BaseModel):
    """Representa um documento exigido para determinado cargo."""

    nome = models.CharField(max_length=255)
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.PROTECT,
        related_name="documentos",
    )

    class Meta:
        """Configurações do modelo DocumentoCargo."""

        verbose_name = "Documento do cargo"
        verbose_name_plural = "Documentos dos cargos"
        ordering = ["nome", "-id"]
        indexes = [
            models.Index(fields=["cargo"]),
        ]
        constraints = [
            models.UniqueConstraint(
                Lower("nome"),
                "cargo",
                condition=models.Q(deletado_em__isnull=True),
                name="documento_cargo_nome_unico",
            ),
        ]

    def __str__(self) -> str:
        """Retorna o nome do documento."""
        return self.nome
