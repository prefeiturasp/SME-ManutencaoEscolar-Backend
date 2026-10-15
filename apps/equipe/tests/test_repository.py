"""Testes do repositório do domínio Equipe."""

import pytest

from apps.equipe.models import Equipe, ProfissionalEquipe
from apps.equipe.repository import (
    EquipeRepository,
    ProfissionalEquipeRepository,
)

pytestmark = pytest.mark.django_db


def test_identifica_equipe_com_mesmo_nome(empresa, lote_centro) -> None:
    """Identifica nome de equipe sem diferenciar maiúsculas."""
    Equipe.objects.create(
        nome="Equipe Elétrica",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )

    existe = EquipeRepository().existe_equipe_empresa(
        "equipe elétrica", empresa.uuid
    )

    assert existe is True


def test_identifica_profissional_inativo(profissional_ativo) -> None:
    """Identifica profissional inativo entre os UUIDs informados."""
    profissional_ativo.status = False
    profissional_ativo.save(update_fields=["status"])

    existem = ProfissionalEquipeRepository().existem_profissionais_inativos(
        [profissional_ativo.uuid]
    )

    assert existem is True


def test_identifica_vinculo_com_equipe_ativa(
    empresa,
    lote_centro,
    profissional_ativo,
    funcao_profissional,
) -> None:
    """Identifica vínculo de profissional com equipe ativa."""
    equipe = Equipe.objects.create(
        nome="Equipe Existente",
        situacao=True,
        empresa=empresa,
        lote=lote_centro,
    )
    ProfissionalEquipe.objects.create(
        equipe=equipe,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )

    repository = ProfissionalEquipeRepository()
    vinculos = repository.obter_vinculos_com_equipes_ativas(
        [profissional_ativo.uuid]
    )

    assert vinculos == [
        (
            profissional_ativo.uuid,
            profissional_ativo.nome,
            equipe.nome,
        )
    ]


def test_nao_persiste_vinculo_sem_alteracoes(
    equipe_existente_ativa,
    profissional_ativo,
    funcao_profissional,
    usuario_ativo,
) -> None:
    """Não altera o vínculo quando os dados permanecem iguais."""
    vinculo = ProfissionalEquipe.objects.create(
        equipe=equipe_existente_ativa,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
        atualizado_por=usuario_ativo,
    )
    atualizado_em = vinculo.atualizado_em

    resultado = ProfissionalEquipeRepository().atualizar(
        vinculo,
        {
            "profissional": profissional_ativo,
            "funcao": funcao_profissional,
        },
        usuario_ativo,
    )

    assert resultado["uuid"] == vinculo.uuid
    vinculo.refresh_from_db()
    assert vinculo.atualizado_em == atualizado_em
