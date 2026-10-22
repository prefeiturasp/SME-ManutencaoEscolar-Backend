"""Testes dos modelos de solicitação de manutenção."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models

from apps.escola.models import Unidadeeducacional
from apps.servico.models import Servico
from apps.solicitacao_manutencao.constants import SituacaoSolicitacao
from apps.solicitacao_manutencao.models import (
    FotoLocalReparo,
    ServicoManutencao,
    SolicitacaoManutencao,
)

pytestmark = pytest.mark.django_db


def _criar_solicitacao(
    unidade_educacional: Unidadeeducacional,
) -> SolicitacaoManutencao:
    """Cria uma solicitação de manutenção para os testes.

    Args:
        unidade_educacional: Unidade vinculada à solicitação.

    Returns:
        Solicitação de manutenção persistida.
    """
    return SolicitacaoManutencao.objects.create(
        codigo="SOL-001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional,
    )


def _criar_servico_manutencao(
    solicitacao: SolicitacaoManutencao,
    servico: Servico | None = None,
) -> ServicoManutencao:
    """Cria um serviço vinculado a uma solicitação.

    Args:
        solicitacao: Solicitação que receberá o serviço.
        servico: Serviço catalogado opcional.

    Returns:
        Serviço de manutenção persistido.
    """
    return ServicoManutencao.objects.create(
        solicitacao_manutencao=solicitacao,
        servico=servico,
        servico_especifico="Troca de disjuntor",
        local_reparo="Cozinha",
        descricao="Disjuntor desarmando constantemente.",
    )


def test_data_envio_permanece_vazia_antes_do_envio(
    unidade_educacional_emef: Unidadeeducacional,
) -> None:
    """Mantém a data vazia enquanto a solicitação não foi enviada."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="SOL-001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )

    assert solicitacao.data_envio is None


def test_nao_preenche_data_envio_ao_alterar_situacao_diretamente(
    unidade_educacional_emef: Unidadeeducacional,
) -> None:
    """Delega à camada de serviço o preenchimento da data de envio."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="SOL-001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )

    solicitacao.situacao = SituacaoSolicitacao.AGUARDANDO_ANALISE_DRE
    solicitacao.save(update_fields=["situacao"])
    solicitacao.refresh_from_db()

    assert solicitacao.data_envio is None


def test_representacao_textual_do_servico_manutencao(
    unidade_educacional_emef: Unidadeeducacional,
) -> None:
    """Exibe o serviço específico e o local do reparo."""
    solicitacao = _criar_solicitacao(unidade_educacional_emef)
    servico_manutencao = _criar_servico_manutencao(solicitacao)

    assert str(servico_manutencao) == "Troca de disjuntor - Cozinha"


def test_metadados_do_servico_manutencao() -> None:
    """Configura os metadados do serviço de manutenção."""
    assert ServicoManutencao._meta.verbose_name == "Serviço de manutenção"
    assert (
        ServicoManutencao._meta.verbose_name_plural == "Serviços de manutenção"
    )
    assert ServicoManutencao._meta.ordering == ["-id"]


def test_relacionamentos_do_servico_manutencao() -> None:
    """Configura os relacionamentos da solicitação e do serviço catalogado."""
    campo_solicitacao = ServicoManutencao._meta.get_field(
        "solicitacao_manutencao"
    )
    campo_servico = ServicoManutencao._meta.get_field("servico")

    assert isinstance(campo_solicitacao, models.ForeignKey)
    assert campo_solicitacao.remote_field.model is SolicitacaoManutencao
    assert campo_solicitacao.remote_field.on_delete is models.CASCADE
    assert campo_solicitacao.remote_field.related_name == "servicos_manutencao"
    assert isinstance(campo_servico, models.ForeignKey)
    assert campo_servico.remote_field.model is Servico
    assert campo_servico.remote_field.on_delete is models.PROTECT
    assert campo_servico.remote_field.related_name == "servicos_manutencao"


def test_foto_local_reparo_e_associada_ao_servico(
    unidade_educacional_emef: Unidadeeducacional,
) -> None:
    """Persiste a foto e a disponibiliza pela relação com o serviço."""
    solicitacao = _criar_solicitacao(unidade_educacional_emef)
    servico_manutencao = _criar_servico_manutencao(solicitacao)
    foto = FotoLocalReparo.objects.create(
        servico_manutencao=servico_manutencao,
        nome_original="reparo.jpg",
        arquivo=SimpleUploadedFile("reparo.jpg", b"conteudo da foto"),
        tipo="imagem",
        tipo_mime="image/jpeg",
        tamanho_bytes=16,
    )

    assert servico_manutencao.fotos.get() == foto
    assert foto.arquivo.name is not None
    assert foto.arquivo.name.startswith("solicitacao_manutencao/anexos/")


def test_metadados_da_foto_local_reparo() -> None:
    """Configura os metadados da foto do local do reparo."""
    assert FotoLocalReparo._meta.verbose_name == "Foto do local do reparo"
    assert (
        FotoLocalReparo._meta.verbose_name_plural == "Fotos do local do reparo"
    )
    assert FotoLocalReparo._meta.ordering == ["-id"]


def test_relacionamento_da_foto_local_reparo() -> None:
    """Configura o relacionamento da foto com o serviço de manutenção."""
    campo = FotoLocalReparo._meta.get_field("servico_manutencao")

    assert isinstance(campo, models.ForeignKey)
    assert campo.remote_field.model is ServicoManutencao
    assert campo.remote_field.on_delete is models.CASCADE
    assert campo.remote_field.related_name == "fotos"
