"""Testes dos modelos relacionados aos tipos de escola."""

import uuid

import pytest
from django.db import IntegrityError

from apps.escola.constants import TIPO_ESCOLA_NAO_ACEITAS
from apps.escola.models.tipos_escola import TipoEscola

pytestmark = pytest.mark.django_db


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

    def test_deve_retornar_apenas_tipos_de_escola_aceitos(self):
        """Deve excluir os tipos de escola não aceitos pelo sistema."""
        sigla_nao_aceita = next(iter(TIPO_ESCOLA_NAO_ACEITAS))

        tipo_aceito = TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )
        tipo_nao_aceito = TipoEscola.objects.create(
            codigo_eol=2,
            sigla=sigla_nao_aceita,
        )

        tipos_aceitos = TipoEscola.objects.aceitos()

        assert tipo_aceito in tipos_aceitos
        assert tipo_nao_aceito not in tipos_aceitos

    def test_deve_retornar_todos_os_tipos_quando_nao_houver_tipo_nao_aceito(
        self,
    ):
        """Deve retornar todos os tipos quando nenhum for não aceito."""
        tipo_emef = TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )
        tipo_cemei = TipoEscola.objects.create(
            codigo_eol=2,
            sigla="CEMEI",
        )

        tipos_aceitos = TipoEscola.objects.aceitos()

        assert list(tipos_aceitos) == [
            tipo_cemei,
            tipo_emef,
        ]

    def test_nao_deve_retornar_tipos_de_escola_nao_aceitos(
        self,
    ):
        """Não deve retornar nenhuma sigla configurada como não aceita."""
        for codigo, sigla in enumerate(TIPO_ESCOLA_NAO_ACEITAS, start=1):
            TipoEscola.objects.create(
                codigo_eol=codigo,
                sigla=sigla,
            )

        assert not TipoEscola.objects.aceitos().exists()
