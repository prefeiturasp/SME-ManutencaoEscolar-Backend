"""Testes dos serializers do domínio Equipe."""

import pytest
from rest_framework.serializers import ValidationError

from apps.equipe.serializers import EquipeCriarSerializer
from apps.profissional.models import Profissional

pytestmark = pytest.mark.django_db


def test_rejeita_equipe_sem_profissionais(equipe_payload) -> None:
    """Exige ao menos um profissional no cadastro."""
    equipe_payload["profissionais"] = []
    serializer = EquipeCriarSerializer(data=equipe_payload)

    assert serializer.is_valid() is False
    assert "profissionais" in serializer.errors


def test_rejeita_nome_formado_apenas_por_espacos() -> None:
    """Não permite nome de equipe formado apenas por espaços."""
    serializer = EquipeCriarSerializer()

    with pytest.raises(ValidationError, match="não pode ser vazio"):
        serializer.validate_nome("   ")


def test_rejeita_profissional_repetido(equipe_payload) -> None:
    """Não permite informar duas vezes o profissional na equipe."""
    equipe_payload["profissionais"].append(
        equipe_payload["profissionais"][0].copy()
    )
    serializer = EquipeCriarSerializer(data=equipe_payload)

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
    serializer = EquipeCriarSerializer(data=equipe_payload)

    assert serializer.is_valid() is False
    assert "funcao" in str(serializer.errors["profissionais"])
