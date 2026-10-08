"""Testes dos serviços do domínio Equipe."""

from typing import Any

import pytest
from django.core.exceptions import ValidationError

from apps.equipe.exceptions import (
    EquipeJaCadastradaError,
    ProfissionaisVinculadosError,
    ProfissionalVinculadoError,
)
from apps.equipe.models import Equipe, ProfissionalEquipe
from apps.equipe.serializers import EquipeCriarSerializer
from apps.equipe.services import EquipeService

pytestmark = pytest.mark.django_db


def _validar_payload(equipe_payload: dict[str, object]) -> dict[str, Any]:
    """Converta o payload da API nos dados esperados pelo serviço."""
    serializer = EquipeCriarSerializer(data=equipe_payload)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def test_cria_equipe_com_profissional(
    equipe_payload: dict[str, object], usuario_ativo
) -> None:
    """Cria a equipe e seu vínculo em uma mesma operação."""
    equipe = EquipeService().criar(
        _validar_payload(equipe_payload), usuario_ativo
    )

    assert equipe.criado_por == usuario_ativo
    assert equipe.profissionais.count() == 1
    assert equipe.profissionais.get().criado_por == usuario_ativo


def test_rejeita_profissional_inativo(
    equipe_payload: dict[str, object], profissional_ativo, usuario_ativo
) -> None:
    """Não permite vincular profissional inativo."""
    profissional_ativo.status = False
    profissional_ativo.save(update_fields=["status"])
    dados_validados = _validar_payload(equipe_payload)
    service = EquipeService()

    with pytest.raises(ValidationError, match="profissional inativo"):
        service.criar(dados_validados, usuario_ativo)

    assert not Equipe.objects.exists()


def test_rejeita_profissional_de_outra_equipe_ativa(
    equipe_payload: dict[str, object],
    erro_profissional_vinculado: dict[str, str],
    usuario_ativo,
) -> None:
    """Não permite profissional que já pertence a equipe ativa."""
    dados_validados = _validar_payload(equipe_payload)
    service = EquipeService()

    with pytest.raises(ProfissionalVinculadoError) as exc_info:
        service.criar(dados_validados, usuario_ativo)

    assert exc_info.value.title == erro_profissional_vinculado["title"]
    assert exc_info.value.detail == erro_profissional_vinculado["detail"]


def test_rejeita_varios_profissionais_vinculados_a_equipes_ativas(
    equipe_payload: dict[str, object],
    erro_varios_profissionais_vinculados: dict[str, object],
    usuario_ativo,
) -> None:
    """Retorna mensagem plural quando vários profissionais têm vínculo."""
    dados_validados = _validar_payload(equipe_payload)
    service = EquipeService()

    with pytest.raises(ProfissionaisVinculadosError) as exc_info:
        service.criar(dados_validados, usuario_ativo)

    assert (
        exc_info.value.title == erro_varios_profissionais_vinculados["title"]
    )
    assert (
        exc_info.value.detail == erro_varios_profissionais_vinculados["detail"]
    )


def test_permite_profissional_de_outra_equipe_inativa(
    equipe_payload: dict[str, object],
    empresa,
    lote_centro,
    profissional_ativo,
    funcao_profissional,
    usuario_ativo,
) -> None:
    """Permite reutilizar profissional cujo vínculo anterior é inativo."""
    equipe_existente = Equipe.objects.create(
        nome="Equipe Existente",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )
    ProfissionalEquipe.objects.create(
        equipe=equipe_existente,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )

    equipe = EquipeService().criar(
        _validar_payload(equipe_payload), usuario_ativo
    )

    assert equipe.profissionais.count() == 1


def test_rejeita_nome_repetido_na_mesma_empresa(
    equipe_payload: dict[str, object],
    empresa,
    lote_centro,
    usuario_ativo,
) -> None:
    """Não permite nome repetido dentro da mesma empresa."""
    Equipe.objects.create(
        nome="equipe elétrica",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )
    dados_validados = _validar_payload(equipe_payload)
    service = EquipeService()

    with pytest.raises(EquipeJaCadastradaError) as exc_info:
        service.criar(dados_validados, usuario_ativo)

    assert exc_info.value.title == "Já existe uma equipe com este nome!"
    assert exc_info.value.detail == (
        "Já existe uma equipe com o nome Equipe Elétrica cadastrada na "
        f"empresa {empresa.nome}. Para cadastrar uma nova equipe, "
        "informe um nome diferente."
    )
