"""Testes dos serializers de solicitação de manutenção."""

from typing import Any

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.solicitacao_manutencao.serializers import (
    FotoLocalReparoSerializer,
    ServicoManutencaoSerializer,
    SolicitacaoManutencaoCriarEditarSerializer,
)

pytestmark = pytest.mark.django_db


def test_exige_arquivo_quando_uuid_nao_e_informado() -> None:
    """Rejeita um item de arquivo sem UUID e sem conteúdo."""
    serializer = FotoLocalReparoSerializer(data={})

    assert not serializer.is_valid()
    assert "arquivo" in serializer.errors


def test_valida_arquivo_informado() -> None:
    """Aceita um novo arquivo quando seu conteúdo é informado."""
    serializer = FotoLocalReparoSerializer(
        data={
            "arquivo": SimpleUploadedFile(
                "reparo.jpg",
                b"conteudo da foto",
                content_type="image/jpeg",
            )
        }
    )

    assert serializer.is_valid(), serializer.errors


def test_rejeita_lista_vazia_de_servicos(
    solicitacao_payload: dict[str, Any],
) -> None:
    """Rejeita explicitamente uma lista vazia de serviços."""
    solicitacao_payload["servicos"] = []
    serializer = SolicitacaoManutencaoCriarEditarSerializer(
        data=solicitacao_payload
    )

    assert not serializer.is_valid()
    assert serializer.errors["servicos"][0] == (
        "Informe ao menos um serviço de manutenção."
    )


def test_exige_ao_menos_um_arquivo_em_cada_servico(
    solicitacao_payload: dict[str, Any],
) -> None:
    """Rejeita serviços cuja lista de arquivos esteja vazia."""
    solicitacao_payload["servicos"][0]["arquivos"] = []
    serializer = SolicitacaoManutencaoCriarEditarSerializer(
        data=solicitacao_payload
    )

    assert not serializer.is_valid()
    assert "arquivos" in serializer.errors["servicos"][0]


def test_rejeita_servico_catalogado_com_servico_especifico(
    solicitacao_payload: dict[str, Any],
) -> None:
    """Rejeita o envio simultâneo das duas formas de informar o serviço."""
    dados_servico = solicitacao_payload["servicos"][0]
    dados_servico["servico_especifico"] = "Troca de disjuntor"
    serializer = SolicitacaoManutencaoCriarEditarSerializer(
        data=solicitacao_payload
    )

    assert not serializer.is_valid()
    assert "servico_especifico" in serializer.errors["servicos"][0]


def test_valida_servico_especifico_sem_servico_catalogado(
    solicitacao_payload: dict[str, Any],
) -> None:
    """Aceita um serviço específico sem serviço catalogado."""
    dados_servico = solicitacao_payload["servicos"][0]
    dados_servico.pop("servico")
    dados_servico["servico_especifico"] = "Troca de disjuntor"
    serializer = SolicitacaoManutencaoCriarEditarSerializer(
        data=solicitacao_payload
    )

    assert serializer.is_valid(), serializer.errors


def test_servico_vazio_e_convertido_para_none(
    solicitacao_payload: dict[str, Any],
) -> None:
    """Converte o serviço catalogado vazio para None."""
    solicitacao_payload["servicos"][0]["servico"] = ""
    solicitacao_payload["servicos"][0]["servico_especifico"] = (
        "Troca de disjuntor"
    )
    serializer = SolicitacaoManutencaoCriarEditarSerializer(
        data=solicitacao_payload
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["servicos"][0]["servico"] is None


def test_normaliza_servico_catalogado_vazio() -> None:
    """Normaliza para None o serviço vazio recebido na validação interna."""
    serializer = ServicoManutencaoSerializer()

    assert serializer.validate({"servico": ""}) == {"servico": None}


def test_valida_servico_catalogado_sem_servico_especifico(
    solicitacao_payload: dict[str, Any],
) -> None:
    """Aceita a seleção de um serviço catalogado sem descrição específica."""
    dados_servico = solicitacao_payload["servicos"][0]
    dados_servico.pop("servico_especifico", None)
    serializer = SolicitacaoManutencaoCriarEditarSerializer(
        data=solicitacao_payload
    )

    assert serializer.is_valid(), serializer.errors
