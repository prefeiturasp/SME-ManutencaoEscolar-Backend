"""Testes para os serializers de Fornecedor."""

from unittest.mock import patch

import pytest
from rest_framework.exceptions import ValidationError

from apps.fornecedor.constants import FornecedorErrorMessages
from apps.fornecedor.serializers import (
    FornecedorCriarSerializer,
    FornecedorSerializer,
)
from apps.utils.exceptions import (
    CepInvalidoError,
    CnpjInvalidoError,
    LinkRastreioInvalidoError,
)

pytestmark = pytest.mark.django_db


class TestFornecedorSerializer:
    """Testes para o serializer de leitura de fornecedor."""

    def test_deve_expor_campos_esperados(self):
        serializer = FornecedorSerializer()

        assert set(serializer.fields.keys()) == {
            "id",
            "nome",
            "cnpj",
            "status",
            "razao_social",
            "link_rastreio",
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "cidade",
            "estado",
        }


class TestFornecedorCriarSerializer:
    """Testes para o serializer de criação de fornecedor."""

    def test_deve_validar_payload_valido(self, fornecedor_payload_valido):
        serializer = FornecedorCriarSerializer(data=fornecedor_payload_valido)

        assert serializer.is_valid()

    @pytest.mark.parametrize(
        ("campo", "valor_invalido"),
        [
            ("cnpj", "123"),
            ("cep", "123"),
            (
                "link_rastreio",
                "link-invalido",
            ),
        ],
    )
    def test_deve_invalidar_campos_formatados(
        self,
        fornecedor_payload_valido,
        campo,
        valor_invalido,
    ):
        payload = {**fornecedor_payload_valido, campo: valor_invalido}
        serializer = FornecedorCriarSerializer(data=payload)

        assert not serializer.is_valid()
        assert campo in serializer.errors

    def test_valida_cnpj_lanca_excecao(self):
        serializer = FornecedorCriarSerializer()

        with (
            patch(
                "apps.fornecedor.serializers.validar_formato_cnpj",
                side_effect=CnpjInvalidoError("erro"),
            ),
            pytest.raises(ValidationError) as exc_info,
        ):
            serializer.validate_cnpj("12345678901234")

        assert (
            exc_info.value.detail[0] == FornecedorErrorMessages.CNPJ_INVALIDO
        )

    def test_valida_cep_lanca_excecao(self):
        serializer = FornecedorCriarSerializer()

        with (
            patch(
                "apps.fornecedor.serializers.validar_formato_cep",
                side_effect=CepInvalidoError("erro"),
            ),
            pytest.raises(ValidationError) as exc_info,
        ):
            serializer.validate_cep("12345678")

        assert exc_info.value.detail[0] == FornecedorErrorMessages.CEP_INVALIDO

    def test_valida_link_rastreio_lanca_excecao(self):
        serializer = FornecedorCriarSerializer()

        with (
            patch(
                "apps.fornecedor.serializers.validar_formato_link_rastreio",
                side_effect=LinkRastreioInvalidoError("erro"),
            ),
            pytest.raises(ValidationError) as exc_info,
        ):
            serializer.validate_link_rastreio(
                "https://www.exemplo.com/rastreio"
            )

        assert exc_info.value.detail[0] == (
            FornecedorErrorMessages.LINK_RASTREIO_INVALIDO
        )

    def test_valida_link_rastreio_com_valor_vazio(self):
        serializer = FornecedorCriarSerializer()

        assert serializer.validate_link_rastreio("") == ""
