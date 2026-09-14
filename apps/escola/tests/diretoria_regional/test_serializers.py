import pytest

from apps.escola.models.diretoria_regional import DiretoriaRegional
from apps.escola.serializers.diretoria_regional_serializers import (
    DiretoriaRegionalSerializer,
)

pytestmark = pytest.mark.django_db


class TestDiretoriaRegionalSerializer:
    """Testes do serializer de Diretoria Regional."""

    def test_deve_serializar_diretoria_regional(self):
        """Deve retornar todos os campos definidos no serializer."""
        diretoria = DiretoriaRegional.objects.create(
            codigo="DRE01",
            nome="DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
            abreviacao="DRE-C",
        )

        serializer = DiretoriaRegionalSerializer(diretoria)

        assert serializer.data == {
            "id": diretoria.id,
            "codigo": "DRE01",
            "nome": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
            "abreviacao": "DRE-C",
            "nome_curto": "DRE BUTANTA",
        }

    def test_deve_retornar_nome_curto_do_model(self):
        """Deve retornar o nome curto calculado pelo model."""
        diretoria = DiretoriaRegional.objects.create(
            codigo="DRE01",
            nome="DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
            abreviacao="DRE-C",
        )

        serializer = DiretoriaRegionalSerializer(diretoria)

        assert serializer.data["nome_curto"] == diretoria.nome_curto

    def test_deve_serializar_nome_sem_prefixo(self):
        """Deve manter o nome quando não possuir o prefixo esperado."""
        diretoria = DiretoriaRegional.objects.create(
            codigo="DRE01",
            nome="DIRETORIA BUTANTA",
            abreviacao="DRE-C",
        )

        serializer = DiretoriaRegionalSerializer(diretoria)

        assert serializer.data["nome_curto"] == "DIRETORIA BUTANTA"

    @pytest.mark.parametrize(
        "campo",
        ["codigo", "nome", "abreviacao"],
    )
    def test_deve_rejeitar_campo_obrigatorio_ausente(self, campo):
        """Deve rejeitar dados sem um dos campos obrigatórios."""
        dados = {
            "codigo": "DRE01",
            "nome": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
            "abreviacao": "DRE-C",
        }
        dados.pop(campo)

        serializer = DiretoriaRegionalSerializer(data=dados)

        assert not serializer.is_valid()
        assert campo in serializer.errors

    def test_deve_rejeitar_codigo_duplicado(self):
        """Deve rejeitar uma diretoria com código já cadastrado."""
        DiretoriaRegional.objects.create(
            codigo="DRE01",
            nome="DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
            abreviacao="DRE-C",
        )

        serializer = DiretoriaRegionalSerializer(
            data={
                "codigo": "DRE01",
                "nome": "DIRETORIA REGIONAL DE EDUCACAO SUL",
                "abreviacao": "DRE-S",
            }
        )

        assert not serializer.is_valid()
        assert "codigo" in serializer.errors
