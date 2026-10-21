"""Modelos do domínio de solicitações de manutenção."""

from django.db import models

from apps.core.models.anexo import Anexo
from apps.core.models.mixins import BaseModel
from apps.solicitacao_manutencao.constants import (
    FaseSolicitacao,
    SituacaoSolicitacao,
    TipoAtendimento,
)


class SolicitacaoManutencao(BaseModel):
    """Representa uma solicitação de manutenção escolar."""

    codigo = models.CharField(max_length=255, unique=True)
    tipo_atendimento = models.CharField(
        max_length=20,
        choices=TipoAtendimento.choices,
    )
    informacoes_adicionais = models.TextField(blank=True, default="")
    unidade_educacional = models.ForeignKey(
        "escola.Unidadeeducacional",
        on_delete=models.PROTECT,
        related_name="solicitacoes_manutencao",
    )
    situacao = models.CharField(
        max_length=30,
        choices=SituacaoSolicitacao.choices,
        default=SituacaoSolicitacao.NAO_ENVIADO_DRE,
    )
    data_envio = models.DateTimeField(null=True, blank=True, editable=False)
    fase = models.CharField(
        max_length=20,
        choices=FaseSolicitacao.choices,
        default=FaseSolicitacao.SOLICITACAO,
    )

    class Meta:
        """Configura os metadados da solicitação."""

        verbose_name = "Solicitação de manutenção"
        verbose_name_plural = "Solicitações de manutenção"
        ordering = ["-id"]

    def __str__(self) -> str:
        """Retorna o código da solicitação."""
        return f"{self.codigo} - {self.unidade_educacional}"


class ServicoManutencao(BaseModel):
    """Representa um serviço incluído em uma solicitação."""

    solicitacao_manutencao = models.ForeignKey(
        SolicitacaoManutencao,
        on_delete=models.CASCADE,
        related_name="servicos_manutencao",
    )
    servico = models.ForeignKey(
        "servico.Servico",
        on_delete=models.PROTECT,
        related_name="servicos_manutencao",
        null=True,
        blank=True,
    )
    servico_especifico = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    local_reparo = models.CharField(max_length=255)
    descricao = models.TextField()

    class Meta:
        """Configura os metadados do serviço de manutenção."""

        verbose_name = "Serviço de manutenção"
        verbose_name_plural = "Serviços de manutenção"
        ordering = ["-id"]

    def __str__(self) -> str:
        """Retorna o serviço específico e o local do reparo."""
        return f"{self.servico_especifico} - {self.local_reparo}"


class FotoLocalReparo(Anexo):
    """Representa uma foto associada a um serviço de manutenção."""

    servico_manutencao = models.ForeignKey(
        ServicoManutencao,
        on_delete=models.CASCADE,
        related_name="fotos",
    )

    class Meta:
        """Configura os metadados da foto do local do reparo."""

        verbose_name = "Foto do local do reparo"
        verbose_name_plural = "Fotos do local do reparo"
        ordering = ["-id"]
