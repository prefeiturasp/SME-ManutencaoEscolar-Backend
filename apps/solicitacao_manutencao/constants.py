"""Escolhas do domínio de solicitações de manutenção."""

from django.db import models

ROTA_VISUALIZAR_SOLICITACAO = "/solicitacao_manutencao/visualizar/{uuid}"


class TipoAtendimento(models.TextChoices):
    """Define os tipos de atendimento de uma solicitação."""

    COMUM = "comum", "Comum"
    URGENTE = "urgente", "Urgente"


class PerfisSolicitacao(models.TextChoices):
    """Define os perfis de usuários solicitantes."""

    UE = "ue", "UE"
    DRE = "dre", "DRE"


class FaseSolicitacao(models.TextChoices):
    """Define as fases de uma solicitação."""

    SOLICITACAO = "solicitacao", "Solicitação"
    VISTORIA = "vistoria", "Vistoria"
    EXECUCAO = "execucao", "Execução"


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


class FaseVistoria(models.TextChoices):
    """Define as fases de vistoria de uma solicitação."""

    VISTORIA_AGUARDANDO = (
        "aguardando_vistoria",
        "Vistoria aguardando agendamento",
    )
    VISTORIA_AGENDADA = "vistoria_agendada", "Vistoria agendada"
    VISTORIA_ATRASADA = "vistoria_atrasada", "Vistoria atrasada"
    VISTORIA_REALIZADA = "vistoria_realizada", "Vistoria realizada"
    VISTORIA_APROVADA = "vistoria_aprovada", "Vistoria aprovada"
    VISTORIA_EM_REVISAO = "vistoria_em_revisao", "Vistoria em revisão"


class FaseExecucao(models.TextChoices):
    """Define as fases de execução de uma solicitação."""

    EXECUCAO_AGUARDANDO = (
        "execucao_aguardando",
        "Execução aguardando agendamento",
    )
    EXECUCAO_AGENDADA = "execucao_agendada", "Execução agendada"
    EXECUCAO_EM_ANDAMENTO = "execucao_em_andamento", "Execução em andamento"
    EXECUCAO_ATRASADA = "execucao_atrasada", "Execução atrasada"
    EXECUCAO_REALIZADA = "execucao_realizada", "Execução realizada"
    EXECUCAO_COM_ATESTE_UE = "execucao_com_ateste_ue", "Execução com ateste UE"
