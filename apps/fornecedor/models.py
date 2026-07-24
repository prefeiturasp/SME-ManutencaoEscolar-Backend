"""Modelos da aplicação Fornecedor."""

from django.db import models

from apps.core.constants import EstadoChoices
from apps.core.models.mixins import BaseModel
from apps.utils.validacoes import (
    apenas_digitos_validator,
    cnpj_formato_validacao,
    link_formato_validacao,
)


class Fornecedor(BaseModel):
    """Representa o cadastro de um fornecedor."""

    nome = models.CharField(max_length=255)
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[cnpj_formato_validacao],
    )
    status = models.BooleanField(default=True)
    razao_social = models.CharField(max_length=255)
    link_rastreio = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        validators=[link_formato_validacao],
    )
    cep = models.CharField(
        max_length=8,
        validators=[apenas_digitos_validator],
    )
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=30)
    complemento = models.CharField(max_length=255, blank=True, default="")
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=EstadoChoices.choices)

    class Meta:
        db_table = "fornecedor"
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["cnpj"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.nome} - {self.cnpj}"
