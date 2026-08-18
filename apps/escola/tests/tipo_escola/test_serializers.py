"""Testes dos serializers do app escola."""

import pytest

from apps.escola.models import TipoEscola
from apps.escola.serializers import TipoEscolaSerializer

pytestmark = pytest.mark.django_db


class TestTipoEscolaSerializer:
    """Testes do serializer de tipos de escola."""

    def test_deve_serializar_tipo_escola(self):
        """Deve serializar corretamente um tipo de escola."""
        tipo_escola = TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )

        serializer = TipoEscolaSerializer(tipo_escola)

        assert serializer.data == {
            "id": tipo_escola.id,
            "uuid": str(tipo_escola.uuid),
            "codigo_eol": 1,
            "sigla": "EMEF",
        }

    def test_deve_validar_dados_validos(self):
        """Deve considerar válidos dados corretos."""
        dados = {
            "codigo_eol": 1,
            "sigla": "EMEF",
        }

        serializer = TipoEscolaSerializer(data=dados)

        assert serializer.is_valid()
        assert serializer.validated_data == {
            "codigo_eol": 1,
            "sigla": "EMEF",
        }

    def test_nao_deve_permitir_codigo_eol_duplicado(self):
        """Não deve permitir código EOL já cadastrado."""
        TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )

        serializer = TipoEscolaSerializer(
            data={
                "codigo_eol": 1,
                "sigla": "EMEI",
            }
        )

        assert not serializer.is_valid()
        assert "codigo_eol" in serializer.errors

    def test_nao_deve_permitir_dados_obrigatorios_ausentes(self):
        """Deve rejeitar dados sem os campos obrigatórios."""
        serializer = TipoEscolaSerializer(data={})

        assert not serializer.is_valid()

        assert "codigo_eol" in serializer.errors
        assert "sigla" in serializer.errors

    def test_nao_deve_permitir_sigla_maior_que_50_caracteres(self):
        """Não deve permitir sigla com mais de 50 caracteres."""
        serializer = TipoEscolaSerializer(
            data={
                "codigo_eol": 1,
                "sigla": "A" * 51,
            }
        )

        assert not serializer.is_valid()
        assert "sigla" in serializer.errors

    def test_nao_deve_permitir_codigo_eol_negativo(self):
        """Não deve permitir código EOL negativo."""
        serializer = TipoEscolaSerializer(
            data={
                "codigo_eol": -1,
                "sigla": "EMEF",
            }
        )

        assert not serializer.is_valid()
        assert "codigo_eol" in serializer.errors

    def test_deve_expor_apenas_os_campos_configurados(self):
        """Deve retornar somente os campos definidos no serializer."""
        tipo_escola = TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )

        serializer = TipoEscolaSerializer(tipo_escola)

        assert set(serializer.data.keys()) == {
            "id",
            "uuid",
            "codigo_eol",
            "sigla",
        }

    def test_nao_deve_permitir_alteracao_do_id_e_uuid(self):
        """Não deve permitir alteração do identificador do registro."""
        tipo_escola = TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEF",
        )

        serializer = TipoEscolaSerializer(
            tipo_escola,
            data={
                "id": tipo_escola.id + 1,
                "uuid": str(tipo_escola.uuid),
                "codigo_eol": 2,
                "sigla": "EMEI",
            },
        )

        assert serializer.is_valid()
        assert serializer.validated_data["codigo_eol"] == 2
        assert serializer.validated_data["sigla"] == "EMEI"
        assert "id" not in serializer.validated_data
        assert "uuid" not in serializer.validated_data
