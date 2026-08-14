"""Modelo referentes ao cargos que tem acesso ao sistema."""

from django.db import models

from apps.usuarios.constants import PerfilAcesso


class CargoEOL(models.Model):
    """
    Modelo responsável por representar os cargos permitidos pelo sistema.

    Cada cargo pertence a um único perfil de acesso.
    """

    codigo = models.CharField(unique=True)

    nome = models.CharField(
        max_length=255,
    )

    perfil = models.CharField(
        max_length=70,
        choices=PerfilAcesso.choices,
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cargo EOL"
        verbose_name_plural = "Cargos EOL"
        ordering = ["nome"]

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nome}"

    def desativar_cargo(self) -> None:
        self.ativo = False
        self.save(update_fields=["ativo"])

    def ativar_cargo(self) -> None:
        self.ativo = True
        self.save(update_fields=["ativo"])

    @property
    def eh_perfil_ue(self) -> bool:
        return self.perfil == PerfilAcesso.UE

    @property
    def eh_perfil_dre(self) -> bool:
        return self.perfil == PerfilAcesso.DRE

    @property
    def eh_perfil_sme(self) -> bool:
        return self.perfil == PerfilAcesso.SME

    @property
    def eh_perfil_empresa(self) -> bool:
        return self.perfil == PerfilAcesso.EMPRESA
