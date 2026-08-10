"""Testes para os serializers de Empresa."""

from unittest.mock import patch

import pytest
from rest_framework.exceptions import ValidationError

from apps.core.exceptions import (
    CepInvalidoError,
    CnpjInvalidoError,
    LinkRastreioInvalidoError,
)
from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.serializers import (
    EmpresaCriarSerializer,
    EmpresaSerializer,
)

pytestmark = pytest.mark.django_db


class TestEmpresaSerializer:
    """Testes para o serializer de leitura de empresa."""

    def test_deve_expor_campos_esperados(self):
        serializer = EmpresaSerializer()

        assert set(serializer.fields.keys()) == {
            "id",
            "uuid",
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


class TestEmpresaCriarSerializer:
    """Testes para o serializer de criação de empresa."""

    def test_deve_validar_payload_valido(self, empresa_payload_valido):
        serializer = EmpresaCriarSerializer(data=empresa_payload_valido)

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
        empresa_payload_valido,
        campo,
        valor_invalido,
    ):
        payload = {**empresa_payload_valido, campo: valor_invalido}
        serializer = EmpresaCriarSerializer(data=payload)

        assert not serializer.is_valid()
        assert campo in serializer.errors

    def test_valida_cnpj_lanca_excecao(self):
        serializer = EmpresaCriarSerializer()

        with (
            patch(
                "apps.empresa.serializers.validar_formato_cnpj",
                side_effect=CnpjInvalidoError("erro"),
            ),
            pytest.raises(ValidationError) as exc_info,
        ):
            serializer.validate_cnpj("12345678901234")

        assert exc_info.value.detail[0] == EmpresaErrorMessages.CNPJ_INVALIDO

    def test_valida_cep_lanca_excecao(self):
        serializer = EmpresaCriarSerializer()

        with (
            patch(
                "apps.empresa.serializers.validar_formato_cep",
                side_effect=CepInvalidoError("erro"),
            ),
            pytest.raises(ValidationError) as exc_info,
        ):
            serializer.validate_cep("12345678")

        assert exc_info.value.detail[0] == EmpresaErrorMessages.CEP_INVALIDO

    def test_valida_link_rastreio_lanca_excecao(self):
        serializer = EmpresaCriarSerializer()

        with (
            patch(
                "apps.empresa.serializers.validar_formato_link_rastreio",
                side_effect=LinkRastreioInvalidoError("erro"),
            ),
            pytest.raises(ValidationError) as exc_info,
        ):
            serializer.validate_link_rastreio(
                "https://www.exemplo.com/rastreio"
            )

        assert exc_info.value.detail[0] == (
            EmpresaErrorMessages.LINK_RASTREIO_INVALIDO
        )

    def test_valida_link_rastreio_com_valor_vazio(self):
        serializer = EmpresaCriarSerializer()

        assert serializer.validate_link_rastreio("") == ""
