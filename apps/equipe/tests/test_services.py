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
from apps.profissional.models import FuncaoProfissional, Profissional

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

    with pytest.raises(ValidationError, match="profissional inativo"):
        EquipeService().criar(_validar_payload(equipe_payload), usuario_ativo)

    assert not Equipe.objects.exists()


def test_rejeita_profissional_de_outra_equipe_ativa(
    equipe_payload: dict[str, object],
    empresa,
    lote_centro,
    profissional_ativo,
    funcao_profissional,
    usuario_ativo,
) -> None:
    """Não permite profissional que já pertence a equipe ativa."""
    equipe_existente = Equipe.objects.create(
        nome="Equipe Existente",
        situacao=True,
        empresa=empresa,
        lote=lote_centro,
    )
    ProfissionalEquipe.objects.create(
        equipe=equipe_existente,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )

    with pytest.raises(ProfissionalVinculadoError) as exc_info:
        EquipeService().criar(_validar_payload(equipe_payload), usuario_ativo)

    assert exc_info.value.title == "Profissional já vinculado a uma equipe!"
    assert exc_info.value.detail == (
        f"O profissional {profissional_ativo.nome} já possui vínculo "
        f"com a equipe {equipe_existente.nome}. Para incluir esse "
        "registro, primeiro remova o vínculo atual com a equipe."
    )


def test_rejeita_varios_profissionais_vinculados_a_equipes_ativas(
    equipe_payload: dict[str, object],
    empresa,
    lote_centro,
    profissional_ativo,
    funcao_profissional,
    usuario_ativo,
) -> None:
    """Retorna mensagem plural quando vários profissionais têm vínculo."""
    outro_profissional = Profissional.objects.create(
        nome="Maria Encanadora",
        cpf="98765432101",
        rg="987654321",
        status=True,
    )
    outra_funcao = FuncaoProfissional.objects.create(
        profissional=outro_profissional,
        cargo=funcao_profissional.cargo,
    )
    equipe_existente = Equipe.objects.create(
        nome="Equipe Existente",
        situacao=True,
        empresa=empresa,
        lote=lote_centro,
    )
    ProfissionalEquipe.objects.bulk_create(
        [
            ProfissionalEquipe(
                equipe=equipe_existente,
                profissional=profissional_ativo,
                funcao=funcao_profissional,
            ),
            ProfissionalEquipe(
                equipe=equipe_existente,
                profissional=outro_profissional,
                funcao=outra_funcao,
            ),
        ]
    )
    equipe_payload["profissionais"].append(
        {
            "profissional": str(outro_profissional.uuid),
            "funcao": str(outra_funcao.uuid),
        }
    )

    with pytest.raises(ProfissionaisVinculadosError) as exc_info:
        EquipeService().criar(_validar_payload(equipe_payload), usuario_ativo)

    assert exc_info.value.title == (
        "Profissionais já vinculados a uma ou mais equipes!"
    )
    assert exc_info.value.detail == (
        "Mais de um profissional já possui vínculo com uma ou mais equipes. "
        "Para incluir esse registro, primeiro remova os vínculos atuais."
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

    with pytest.raises(EquipeJaCadastradaError) as exc_info:
        EquipeService().criar(_validar_payload(equipe_payload), usuario_ativo)

    assert exc_info.value.title == "Já existe uma equipe com este nome!"
    assert exc_info.value.detail == (
        "Já existe uma equipe com o nome Equipe Elétrica cadastrada na "
        f"empresa {empresa.nome}. Para cadastrar uma nova equipe, "
        "informe um nome diferente."
    )
