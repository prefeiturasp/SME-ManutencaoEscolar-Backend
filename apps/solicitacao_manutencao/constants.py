"""Escolhas do domínio de solicitações de manutenção."""

from django.db import models


class TipoAtendimento(models.TextChoices):
    """Define os tipos de atendimento de uma solicitação."""

    COMUM = "comum", "Comum"
    URGENTE = "urgente", "Urgente"


class PerfisSolicitacao(models.TextChoices):
    """Define os perfis de usuários solicitantes."""

    UE = "ue", "UE"


class SituacaoSolicitacao(models.TextChoices):
    """Define as situações de uma solicitação."""

    NAO_ENVIADO_DRE = "nao_enviado_dre", "Não enviada para a DRE"
    AGUARDANDO_ANALISE_DRE = (
        "aguardando_analise_dre",
        "Aguardando Análise da DRE",
    )
    APROVADA_DRE = "aprovada_dre", "Aprovada (DRE)"
    REPROVADA_DRE = "reprovada_dre", "Reprovada (DRE)"
    NECESSIDADE_REVISAO_UE = (
        "necessidade_revisao_ue",
        "Necessidade de revisão (UE)",
    )
    AGUARDANDO_ANALISE_GME_SME = (
        "aguardando_analise_gme_sme",
        "Aguardando análise GME/SME",
    )
    APROVADA_GME_SME = "aprovada_gme_sme", "Aprovada (GME/SME)"
    REPROVADA_GME_SME = "reprovada_gme_sme", "Reprovada (GME/SME)"
    NECESSIDADE_REVISAO_DRE = (
        "necessidade_revisao_dre",
        "Necessidade de revisão (DRE)",
    )


class FaseSolicitacao(models.TextChoices):
    """Define as fases de uma solicitação."""

    SOLICITACAO = "solicitacao", "Solicitação"
    VISTORIA = "vistoria", "Vistoria"
    EXECUCAO = "execucao", "Execução"
