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
from apps.empresa.serializers.empresa_serializers import (
    EmpresaCriarAtualizarSerializer,
    EmpresaSerializer,
)
from apps.empresa.serializers.responsavel_serializers import (
    ResponsavelTecnicoSerializer,
)

pytestmark = pytest.mark.django_db


class TestEmpresaSerializer:
    """Testes para o serializer de leitura de empresa."""

    def test_deve_expor_campos_esperados(self):
        """Deve expor os campos esperados."""
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
            "criado_por",
            "criado_em",
            "atualizado_por",
            "atualizado_em",
        }


class TestEmpresaCriarAtualizarSerializer:
    """Testes para o serializer de criação de empresa."""

    def test_deve_validar_payload_valido(self, empresa_payload_valido):
        """Deve validar um payload válido."""
        serializer = EmpresaCriarAtualizarSerializer(
            data=empresa_payload_valido
        )

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
        """Deve invalidar campos com formato incorreto."""
        payload = {**empresa_payload_valido, campo: valor_invalido}
        serializer = EmpresaCriarAtualizarSerializer(data=payload)

        assert not serializer.is_valid()
        assert campo in serializer.errors

    def test_valida_cnpj_lanca_excecao(self):
        """Deve lançar exceção ao validar CNPJ inválido."""
        serializer = EmpresaCriarAtualizarSerializer()

        with (
            patch(
                "apps.empresa.serializers.empresa_serializers.validar_formato_cnpj",
                side_effect=CnpjInvalidoError("erro"),
            ),
            pytest.raises(ValidationError) as exc_info,
        ):
            serializer.validate_cnpj("12345678901234")

        assert exc_info.value.detail[0] == EmpresaErrorMessages.CNPJ_INVALIDO

    def test_valida_cep_lanca_excecao(self):
        """Deve lançar exceção ao validar CEP inválido."""
        serializer = EmpresaCriarAtualizarSerializer()

        with (
            patch(
                "apps.empresa.serializers.empresa_serializers.validar_formato_cep",
                side_effect=CepInvalidoError("erro"),
            ),
            pytest.raises(ValidationError) as exc_info,
        ):
            serializer.validate_cep("12345678")

        assert exc_info.value.detail[0] == EmpresaErrorMessages.CEP_INVALIDO

    def test_valida_link_rastreio_lanca_excecao(self):
        """Deve lançar exceção ao validar link de rastreio inválido."""
        serializer = EmpresaCriarAtualizarSerializer()

        with (
            patch(
                "apps.empresa.serializers.empresa_serializers.validar_formato_link_rastreio",
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
        """Deve permitir link de rastreio vazio."""
        serializer = EmpresaCriarAtualizarSerializer()

        assert serializer.validate_link_rastreio("") == ""


class TestResponsavelTecnicoSerializer:
    """Testes para o serializer de responsável técnico."""

    def test_deve_validar_payload_com_uuid_da_empresa(self, empresa):
        """Deve aceitar o uuid da empresa como referência."""
        serializer = ResponsavelTecnicoSerializer(
            data={
                "empresa": str(empresa.uuid),
                "nome": "João Responsável",
                "tipo": "preposto",
                "email": "joao.responsavel@email.com",
            }
        )

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["empresa"] == empresa

    def test_deve_invalidar_uuid_de_empresa_inexistente(self, empresa):
        """Deve invalidar quando o uuid não corresponde a nenhuma empresa."""
        serializer = ResponsavelTecnicoSerializer(
            data={
                "empresa": "00000000-0000-0000-0000-000000000000",
                "nome": "João Responsável",
                "tipo": "preposto",
                "email": "joao.responsavel@email.com",
            }
        )

        assert not serializer.is_valid()
        assert "empresa" in serializer.errors

    def test_valida_empresa_com_valor_vazio_lanca_excecao(self):
        """Deve lançar exceção quando o valor da empresa for inválido."""
        serializer = ResponsavelTecnicoSerializer()

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_empresa(None)

        assert exc_info.value.detail[0] == (
            EmpresaErrorMessages.EMPRESA_INVALIDA
        )

    def test_deve_invalidar_id_numerico_da_empresa(self, empresa):
        """Deve invalidar o id numérico, pois a referência é feita por uuid."""
        serializer = ResponsavelTecnicoSerializer(
            data={
                "empresa": empresa.id,
                "nome": "João Responsável",
                "tipo": "preposto",
                "email": "joao.responsavel@email.com",
            }
        )

        assert not serializer.is_valid()
        assert "empresa" in serializer.errors
