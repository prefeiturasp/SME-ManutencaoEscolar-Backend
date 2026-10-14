"""Testes dos serializers do domínio Equipe."""

from datetime import date

import pytest
from rest_framework.serializers import ValidationError

from apps.empresa.models import Empresa
from apps.equipe.models import ProfissionalEquipe
from apps.equipe.serializers import (
    EquipeCriarEditarSerializer,
    EquipeListSerializer,
    EquipeSerializer,
)
from apps.profissional.models import FuncaoProfissional, Profissional

pytestmark = pytest.mark.django_db


def test_lista_equipe_com_dados_resumidos_do_lote(
    equipe_existente_ativa,
) -> None:
    """Retorna nome e período do lote na listagem de equipes."""
    equipe_existente_ativa.lote.periodo_inicial = date(2026, 1, 1)
    equipe_existente_ativa.lote.periodo_final = date(2026, 12, 31)
    equipe_existente_ativa.lote.save(
        update_fields=["periodo_inicial", "periodo_final"]
    )

    resultado = EquipeListSerializer(equipe_existente_ativa).data

    assert resultado["lote"] == {
        "uuid": str(equipe_existente_ativa.lote.uuid),
        "nome": equipe_existente_ativa.lote.nome,
        "periodo_inicial": "2026-01-01",
        "periodo_final": "2026-12-31",
    }


def test_detalha_equipe_com_empresa_lote_e_profissionais(
    equipe_existente_ativa,
    profissional_ativo: Profissional,
    funcao_profissional: FuncaoProfissional,
) -> None:
    """Retorna os dados relacionados no detalhe da equipe."""
    ProfissionalEquipe.objects.create(
        equipe=equipe_existente_ativa,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )

    resultado = EquipeSerializer(equipe_existente_ativa).data

    assert resultado["empresa"] == {
        "uuid": str(equipe_existente_ativa.empresa.uuid),
        "nome": equipe_existente_ativa.empresa.nome,
        "cnpj": equipe_existente_ativa.empresa.cnpj,
    }
    assert resultado["lote"] == {
        "uuid": str(equipe_existente_ativa.lote.uuid),
        "nome": equipe_existente_ativa.lote.nome,
        "periodo_inicial": None,
        "periodo_final": None,
    }
    assert resultado["profissionais"] == [
        {
            "profissional": profissional_ativo.uuid,
            "cpf": profissional_ativo.cpf,
            "nome": profissional_ativo.nome,
            "funcao": funcao_profissional.uuid,
            "nome_funcao": funcao_profissional.cargo.nome,
        }
    ]


def test_rejeita_equipe_sem_profissionais(equipe_payload) -> None:
    """Exige ao menos um profissional no cadastro."""
    equipe_payload["profissionais"] = []
    serializer = EquipeCriarEditarSerializer(data=equipe_payload)

    assert serializer.is_valid() is False
    assert "profissionais" in serializer.errors


def test_rejeita_nome_formado_apenas_por_espacos() -> None:
    """Não permite nome de equipe formado apenas por espaços."""
    serializer = EquipeCriarEditarSerializer()

    with pytest.raises(ValidationError, match="não pode ser vazio"):
        serializer.validate_nome("   ")


def test_rejeita_profissional_repetido(equipe_payload) -> None:
    """Não permite informar duas vezes o profissional na equipe."""
    equipe_payload["profissionais"].append(
        equipe_payload["profissionais"][0].copy()
    )
    serializer = EquipeCriarEditarSerializer(data=equipe_payload)

    assert serializer.is_valid() is False
    assert "profissionais" in serializer.errors


def test_rejeita_funcao_de_outro_profissional(
    equipe_payload, funcao_profissional
) -> None:
    """Exige que a função pertença ao profissional informado."""
    outro = Profissional.objects.create(
        nome="Outro Profissional",
        cpf="98765432101",
        rg="987654321",
    )
    equipe_payload["profissionais"][0]["profissional"] = str(outro.uuid)
    serializer = EquipeCriarEditarSerializer(data=equipe_payload)

    assert serializer.is_valid() is False
    assert "funcao" in str(serializer.errors["profissionais"])


def test_rejeita_empresa_nao_associada_ao_lote(equipe_payload) -> None:
    """Exige que a empresa informada seja a empresa do lote selecionado."""
    outra_empresa = Empresa.objects.create(nome="Outra empresa")
    equipe_payload["empresa"] = str(outra_empresa.uuid)
    serializer = EquipeCriarEditarSerializer(data=equipe_payload)

    assert serializer.is_valid() is False
    assert serializer.errors["empresa"] == [
        "A empresa informada não está associada ao lote selecionado."
    ]


def test_valida_atualizacao_parcial_sem_empresa_e_lote(
    equipe_existente_ativa,
) -> None:
    """Permite omitir empresa e lote em uma atualização parcial."""
    serializer = EquipeCriarEditarSerializer(
        equipe_existente_ativa,
        data={"nome": "Equipe Atualizada"},
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors
