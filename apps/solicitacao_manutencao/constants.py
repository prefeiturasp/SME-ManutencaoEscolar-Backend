"""Escolhas do domínio de solicitações de manutenção."""

from django.db import models


class TipoAtendimento(models.TextChoices):
    """Define os tipos de atendimento de uma solicitação."""

    COMUM = "comum", "Comum"
    URGENTE = "urgente", "Urgente"


class SituacaoSolicitacao(models.TextChoices):
    """Define as situações de uma solicitação."""

    NAO_ENVIADO_DRE = "nao_enviado_dre", "Não enviado para a DRE"
    AGUARDANDO_ANALISE_DRE = (
        "aguardando_analise_dre",
        "Aguardando Análise de DRE",
    )


class FaseSolicitacao(models.TextChoices):
    """Define as fases de uma solicitação."""

    SOLICITACAO = "solicitacao", "Solicitação"
