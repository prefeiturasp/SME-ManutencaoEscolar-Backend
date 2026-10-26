"""Constantes do app usuarios."""

from django.db import models

ENDPOINT_CARGOS_EOL = "/cargos"


class PerfilAcesso(models.TextChoices):
    """Perfis de acesso disponíveis no sistema."""

    UE = "UE", "Diretor Unidade Educarional"
    DRE = "DRE", "Diretoria Regional de Educação"
    SME = "SME", "SME / GME"
    EMPRESA = "EMPRESA", "Empresa"
