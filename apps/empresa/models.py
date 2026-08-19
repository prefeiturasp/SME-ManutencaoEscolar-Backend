"""Modelos da aplicação Empresa."""

from django.db import models

from apps.core.constants import EstadoChoices
from apps.core.models.mixins import BaseModel
from apps.core.validacoes import (
    apenas_digitos_validator,
    cnpj_formato_validacao,
    link_formato_validacao,
)


class Empresa(BaseModel):
    """Representa o cadastro de uma empresa."""

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
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["-status", "-id"]
        indexes = [
            models.Index(fields=["cnpj"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.nome} - {self.cnpj}"


class ResponsavelTecnico(BaseModel):
    """Representa o cadastro de um responsável técnico de uma empresa."""

    TIPO_RESPONSAVEL_CHOICES = [
        ("preposto", "Preposto"),
        ("engenheiro_civil", "Engenheiro Civil"),
        ("engenheiro_eletricista", "Engenheiro Eletricista"),
    ]

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="responsaveis_tecnicos",
    )
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=TIPO_RESPONSAVEL_CHOICES)
    numero_crea = models.CharField(max_length=20, blank=True, default="")
    numero_art = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        verbose_name = "Responsável Técnico"
        verbose_name_plural = "Responsáveis Técnicos"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.nome} - {self.tipo}"
