"""Testes do repositório do domínio Equipe."""

from types import SimpleNamespace
from unittest.mock import MagicMock

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


def test_equipe_sem_vinculos_externos_nao_bloqueia_exclusao(
    equipe_existente_ativa, profissional_vinculado
) -> None:
    """Ignora os profissionais da própria equipe ao buscar vínculos."""
    possui = EquipeRepository().possui_vinculos_externos(
        equipe_existente_ativa
    )

    assert possui is False


def test_identifica_vinculo_externo_ativo(
    monkeypatch, equipe_existente_ativa
) -> None:
    """Identifica outro cadastro que referencia a equipe."""
    gerenciador = MagicMock()
    gerenciador.filter.return_value.exists.return_value = True
    relacao = SimpleNamespace(
        related_model=SimpleNamespace(_default_manager=gerenciador),
        field=SimpleNamespace(name="equipe"),
    )
    monkeypatch.setattr(Equipe._meta, "related_objects", (relacao,))

    possui = EquipeRepository().possui_vinculos_externos(
        equipe_existente_ativa
    )

    assert possui is True
    gerenciador.filter.assert_called_once_with(equipe=equipe_existente_ativa)


def test_ignora_vinculo_externo_inexistente(
    monkeypatch, equipe_existente_ativa
) -> None:
    """Não considera vinculada a equipe sem registros que a referenciem."""
    gerenciador = MagicMock()
    gerenciador.filter.return_value.exists.return_value = False
    relacao = SimpleNamespace(
        related_model=SimpleNamespace(_default_manager=gerenciador),
        field=SimpleNamespace(name="equipe"),
    )
    monkeypatch.setattr(Equipe._meta, "related_objects", (relacao,))

    possui = EquipeRepository().possui_vinculos_externos(
        equipe_existente_ativa
    )

    assert possui is False


def test_deleta_equipe_e_vinculos_dos_profissionais(
    equipe_existente_ativa, profissional_vinculado, usuario_ativo
) -> None:
    """Exclui logicamente a equipe e os vínculos com seus profissionais."""
    EquipeRepository().deletar(equipe_existente_ativa, usuario_ativo)

    assert not Equipe.objects.filter(pk=equipe_existente_ativa.pk).exists()
    equipe = Equipe.dm_objects.get(pk=equipe_existente_ativa.pk)
    assert equipe.deletado_em is not None
    assert equipe.deletado_por == usuario_ativo
    vinculo = ProfissionalEquipe.dm_objects.get(pk=profissional_vinculado.pk)
    assert vinculo.deletado_em is not None
    assert vinculo.deletado_por == usuario_ativo
