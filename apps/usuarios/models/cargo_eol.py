"""_summary_."""

import datetime

from django.db import models


class PerfilAcesso(models.TextChoices):
    """Perfis de acesso disponíveis no sistema."""

    UE = "UE", "Unidade Escolar"
    DRE = "DRE", "Diretoria Regional de Educação"
    SME = "SME", "SME / GME"
    EMPRESA = "EMPRESA", "Empresa"


class CargoEOL(models.Model):
    """
    Modelo responsável por representar os cargos permitidos pelo sistema.

    Cada cargo pertence a um único perfil de acesso.
    """

    codigo = models.PositiveIntegerField(
        unique=True,
        verbose_name="Código do Cargo",
    )

    nome = models.CharField(
        max_length=255,
    )

    perfil = models.CharField(
        max_length=20,
        choices=PerfilAcesso.choices,
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cargo EOL"
        verbose_name_plural = "Cargos EOL"
        ordering = ["nome"]

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nome}"

    def finalizar_cargo(self) -> None:
        self.ativo = False
        self.data_final = datetime.date.today()
        self.save()

    def ativar_cargo(self) -> None:
        self.ativo = True
        self.data_inicial = datetime.date.today()
        self.save()
