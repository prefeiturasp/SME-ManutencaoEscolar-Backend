"""Constantes do app usuarios."""

from django.db import models

ENDPOINT_CARGOS_EOL = "/cargos"


class PerfilAcesso(models.TextChoices):
    """Perfis de acesso disponíveis no sistema."""

    UE = "UE", "Unidade Educacional"
    DRE = "DRE", "Diretoria Regional de Educação"
    SME = "SME", "GME/SME"
    EMPRESA = "EMPRESA", "Empresa"


class Funcionalidade(models.TextChoices):
    """Funcionalidades do sistema controladas por permissão de acesso."""

    CADASTROS = "CADASTROS", "Cadastros (todos os recursos)"
    SOLICITACAO_MANUTENCAO = (
        "SOLICITACAO_MANUTENCAO",
        "Solicitação de manutenção",
    )
    RELATORIOS = "RELATORIOS", "Relatórios"


FUNCIONALIDADES_POR_PERFIL: dict[str, frozenset[str]] = {
    PerfilAcesso.SME: frozenset(
        {
            Funcionalidade.CADASTROS,
            Funcionalidade.RELATORIOS,
        }
    ),
    PerfilAcesso.DRE: frozenset(
        {
            Funcionalidade.RELATORIOS,
            Funcionalidade.SOLICITACAO_MANUTENCAO,
        }
    ),
    PerfilAcesso.UE: frozenset(
        {Funcionalidade.SOLICITACAO_MANUTENCAO, Funcionalidade.RELATORIOS}
    ),
    PerfilAcesso.EMPRESA: frozenset({Funcionalidade.RELATORIOS}),
}
