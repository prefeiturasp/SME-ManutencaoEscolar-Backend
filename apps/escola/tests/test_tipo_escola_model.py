"""Testes dos modelos relacionados aos tipos de escola."""

import uuid

import pytest
from django.db import IntegrityError

from apps.escola.models.tipos_escola import TipoEscola


@pytest.mark.django_db
class TestTipoEscola:
    """Testes do model TipoEscola."""

    def test_deve_criar_tipo_escola_com_dados_validos(self):
        """Deve criar um tipo de escola com os dados informados."""
        tipo_escola = TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )

        assert tipo_escola.codigo_eol == 1
        assert tipo_escola.sigla == "EMEF"

    def test_deve_gerar_uuid_automaticamente(self):
        """Deve gerar um UUID automaticamente para o registro."""
        tipo_escola = TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )

        assert tipo_escola.uuid is not None
        assert isinstance(tipo_escola.uuid, uuid.UUID)

    def test_deve_representar_tipo_escola_com_str(self):
        """Deve retornar código e sigla na representação textual."""
        tipo_escola = TipoEscola(
            codigo_eol=1,
            sigla="EMEF",
        )

        assert str(tipo_escola) == "1 - EMEF"

    def test_nao_deve_permitir_codigo_eol_duplicado(self):
        """Não deve permitir dois registros com o mesmo código EOL."""
        TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )

        with pytest.raises(IntegrityError):
            TipoEscola.objects.create(
                codigo_eol=1,
                sigla="EMEI",
            )

    def test_deve_ordenar_por_sigla(self):
        """Deve retornar os tipos de escola ordenados pela sigla."""
        tipo_emei = TipoEscola.objects.create(
            codigo_eol=2,
            sigla="EMEI",
        )
        tipo_emef = TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )
        tipo_ceu = TipoEscola.objects.create(
            codigo_eol=3,
            sigla="CEU",
        )

        tipos_escola = list(TipoEscola.objects.all())

        assert tipos_escola == [
            tipo_ceu,
            tipo_emef,
            tipo_emei,
        ]
