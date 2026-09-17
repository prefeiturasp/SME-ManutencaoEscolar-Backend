"""Modelos do domínio Profissional."""

from django.db import models

from apps.cargo.models import Cargo
from apps.core.models.mixins import BaseModel
from apps.profissional.constants import ProfissionalErrorMessages


class Profissional(BaseModel):
    """Representa o cadastro de um profissional."""

    nome = models.CharField(max_length=255)
    rg = models.CharField(max_length=20)
    cpf = models.CharField(max_length=11)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"
        ordering = ["-status", "-id"]
        indexes = [
            models.Index(fields=["rg"]),
            models.Index(fields=["cpf"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["cpf"],
                condition=models.Q(deletado_em__isnull=True),
                name="profissional_cpf_unico",
                violation_error_message=ProfissionalErrorMessages.PROFISSIONAL_CPF_JA_CADASTRADO,
            ),
            models.UniqueConstraint(
                fields=["rg"],
                condition=models.Q(deletado_em__isnull=True),
                name="profissional_rg_unico",
                violation_error_message=ProfissionalErrorMessages.PROFISSIONAL_RG_JA_CADASTRADO,
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nome} - {self.cpf}"


class FuncaoProfissional(BaseModel):
    """Representa uma função exercida por um profissional."""

    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.CASCADE,
        related_name="funcoes",
    )
    profissional = models.ForeignKey(
        Profissional,
        on_delete=models.CASCADE,
        related_name="funcoes",
    )

    class Meta:
        verbose_name = "Função do Profissional"
        verbose_name_plural = "Funções dos Profissionais"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["cargo", "profissional"],
                condition=models.Q(deletado_em__isnull=True),
                name="funcao_profissional_cargo_unico",
                violation_error_message=ProfissionalErrorMessages.FUNCAO_PROFISSIONAL_JA_CADASTRADA,
            )
        ]

    def __str__(self) -> str:
        return f"{self.profissional.nome} - {self.cargo.nome}"


class DocumentoFuncaoProfissional(BaseModel):
    """Representa um documento exigido para uma função profissional."""

    nome = models.CharField(max_length=255)
    funcao_profissional = models.ForeignKey(
        FuncaoProfissional,
        on_delete=models.CASCADE,
        related_name="documentos",
    )

    class Meta:
        verbose_name = "Documento da Função profissional"
        verbose_name_plural = "Documentos das Funções profissionais"
        ordering = ["nome", "-id"]

    def __str__(self) -> str:
        return f"{self.nome} - {self.funcao_profissional}"
