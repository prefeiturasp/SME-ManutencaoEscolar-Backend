"""Testes dos serializers de unidades educacionais."""

import pytest

from apps.escola.serializers.unidade_educacional_serializers import (
    UnidadeEducacionalSerializer,
)

pytestmark = pytest.mark.django_db


class TestUnidadeEducacionalSerializer:
    """Testa o serializer de unidades educacionais."""

    def test_deve_retornar_none_quando_dre_nao_possuir_vinculo_lote(
        self,
        unidade_educacional_emef,
    ):
        """Deve retornar None quando a DRE não possui lote associado."""
        serializer = UnidadeEducacionalSerializer()

        resultado = serializer.get_lote(unidade_educacional_emef)

        assert resultado is None

    def test_deve_retornar_lote_quando_dre_possuir_vinculo_lote(
        self,
        unidade_educacional_emef,
        lote_centro,
    ):
        """Deve retornar os dados do lote associado à DRE."""
        serializer = UnidadeEducacionalSerializer()

        resultado = serializer.get_lote(unidade_educacional_emef)

        assert resultado == {
            "id": lote_centro.id,
            "uuid": str(lote_centro.uuid),
            "codigo_cadastro": lote_centro.codigo_cadastro,
            "nome": lote_centro.nome,
            "status": lote_centro.status,
        }
