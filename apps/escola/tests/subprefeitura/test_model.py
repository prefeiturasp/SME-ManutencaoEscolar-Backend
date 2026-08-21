"""Testes do model Subprefeitura."""

import uuid

import pytest
from django.db import IntegrityError

from apps.escola.models import Subprefeitura

pytestmark = pytest.mark.django_db


class TestSubprefeitura:
    """Testes do model Subprefeitura."""

    def test_deve_criar_subprefeitura_com_dados_validos(self):
        """Deve criar uma Subprefeitura com os dados informados."""
        subprefeitura = Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
        )

        assert subprefeitura.codigo_eol == "SP01"
        assert subprefeitura.nome == "Subprefeitura Sé"

    def test_deve_gerar_uuid_automaticamente(self):
        """Deve gerar um UUID automaticamente para o registro."""
        subprefeitura = Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
        )

        assert subprefeitura.uuid is not None
        assert isinstance(subprefeitura.uuid, uuid.UUID)

    def test_deve_representar_subprefeitura_com_str(self):
        """Deve retornar código e nome na representação textual."""
        subprefeitura = Subprefeitura(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
        )

        assert str(subprefeitura) == "SP01 - Subprefeitura Sé"

    def test_nao_deve_permitir_codigo_eol_duplicado(self):
        """Não deve permitir dois registros com o mesmo código EOL."""
        Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
        )

        with pytest.raises(IntegrityError):
            Subprefeitura.objects.create(
                codigo_eol="SP01",
                nome="Subprefeitura Lapa",
            )

    def test_deve_ordenar_por_nome(self):
        """Deve retornar as Subprefeituras ordenadas pelo nome."""
        subprefeitura_se = Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
        )
        subprefeitura_lapa = Subprefeitura.objects.create(
            codigo_eol="SP02",
            nome="Subprefeitura Lapa",
        )
        subprefeitura_mooca = Subprefeitura.objects.create(
            codigo_eol="SP03",
            nome="Subprefeitura Mooca",
        )

        subprefeituras = list(Subprefeitura.objects.all())

        assert subprefeituras == [
            subprefeitura_lapa,
            subprefeitura_mooca,
            subprefeitura_se,
        ]
