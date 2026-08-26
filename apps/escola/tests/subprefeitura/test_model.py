"""Testes do model Subprefeitura."""

import uuid

import pytest
from django.db import IntegrityError

from apps.escola.models import Subprefeitura

pytestmark = pytest.mark.django_db


class TestSubprefeitura:
    """Testes do model Subprefeitura."""

    def test_deve_criar_subprefeitura_com_dados_validos(
        self, diretoria_regional_centro
    ):
        """Deve criar uma Subprefeitura com os dados informados."""
        subprefeitura = Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
            diretoria_regional=diretoria_regional_centro,
        )

        assert subprefeitura.codigo_eol == "SP01"
        assert subprefeitura.nome == "Subprefeitura Sé"

    def test_deve_gerar_uuid_automaticamente(self, diretoria_regional_centro):
        """Deve gerar um UUID automaticamente para o registro."""
        subprefeitura = Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
            diretoria_regional=diretoria_regional_centro,
        )

        assert subprefeitura.uuid is not None
        assert isinstance(subprefeitura.uuid, uuid.UUID)

    def test_deve_representar_subprefeitura_com_str(
        self, diretoria_regional_centro
    ):
        """Deve retornar código e nome na representação textual."""
        subprefeitura = Subprefeitura(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
            diretoria_regional=diretoria_regional_centro,
        )

        assert str(subprefeitura) == "SP01 - Subprefeitura Sé"

    def test_nao_deve_permitir_codigo_eol_duplicado(
        self,
        diretoria_regional_centro,
    ):
        """Não deve permitir dois registros com o mesmo código EOL."""
        Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
            diretoria_regional=diretoria_regional_centro,
        )

        with pytest.raises(IntegrityError):
            Subprefeitura.objects.create(
                codigo_eol="SP01",
                nome="Subprefeitura Lapa",
            )

    def test_deve_ordenar_por_nome(self, diretoria_regional_centro):
        """Deve retornar as Subprefeituras ordenadas pelo nome."""
        subprefeitura_se = Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
            diretoria_regional=diretoria_regional_centro,
        )
        subprefeitura_lapa = Subprefeitura.objects.create(
            codigo_eol="SP02",
            nome="Subprefeitura Lapa",
            diretoria_regional=diretoria_regional_centro,
        )
        subprefeitura_mooca = Subprefeitura.objects.create(
            codigo_eol="SP03",
            nome="Subprefeitura Mooca",
            diretoria_regional=diretoria_regional_centro,
        )

        subprefeituras = list(Subprefeitura.objects.all())

        assert subprefeituras == [
            subprefeitura_lapa,
            subprefeitura_mooca,
            subprefeitura_se,
        ]
