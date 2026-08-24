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

    def test_deve_validar_payload_valido(
        self, empresa_payload_valido_com_responsaveis
    ):
        """Deve validar um payload válido."""
        serializer = EmpresaCriarAtualizarSerializer(
            data=empresa_payload_valido_com_responsaveis
        )

        assert serializer.is_valid(), serializer.errors

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
        empresa_payload_valido_com_responsaveis,
        campo,
        valor_invalido,
    ):
        """Deve invalidar campos com formato incorreto."""
        payload = {
            **empresa_payload_valido_com_responsaveis,
            campo: valor_invalido,
        }
        serializer = EmpresaCriarAtualizarSerializer(data=payload)

        assert not serializer.is_valid()
        assert campo in serializer.errors

    def test_deve_invalidar_quando_responsaveis_tecnicos_ausente(
        self, empresa_payload_valido
    ):
        """Deve invalidar quando responsáveis técnicos não forem informados."""
        serializer = EmpresaCriarAtualizarSerializer(
            data=empresa_payload_valido
        )

        assert not serializer.is_valid()
        assert "responsaveis_tecnicos" in serializer.errors

    def test_deve_invalidar_quando_responsaveis_tecnicos_vazio(
        self, empresa_payload_valido_com_responsaveis
    ):
        """Deve invalidar quando a lista de responsáveis técnicos for vazia."""
        payload = {
            **empresa_payload_valido_com_responsaveis,
            "responsaveis_tecnicos": [],
        }
        serializer = EmpresaCriarAtualizarSerializer(data=payload)

        assert not serializer.is_valid()
        assert serializer.errors["responsaveis_tecnicos"][0] == (
            "Informe ao menos um responsável técnico."
        )

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

    def test_valida_responsaveis_tecnicos_com_lista_vazia_lanca_excecao(self):
        """Deve lançar exceção ao validar lista vazia de responsáveis."""
        serializer = EmpresaCriarAtualizarSerializer()

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_responsaveis_tecnicos([])

        assert exc_info.value.detail[0] == (
            "Informe ao menos um responsável técnico."
        )


class TestResponsavelTecnicoSerializer:
    """Testes para o serializer de responsável técnico."""

    def test_deve_expor_campos_esperados(self):
        """Deve expor os campos esperados."""
        serializer = ResponsavelTecnicoSerializer()

        assert set(serializer.fields.keys()) == {
            "tipo",
            "nome",
            "email",
            "numero_crea",
            "telefone",
            "numero_art",
            "criado_por",
            "criado_em",
            "atualizado_por",
            "atualizado_em",
        }

    def test_deve_validar_payload_valido(
        self, responsavel_tecnico_payload_valido
    ):
        """Deve validar um payload válido."""
        serializer = ResponsavelTecnicoSerializer(
            data=responsavel_tecnico_payload_valido
        )

        assert serializer.is_valid(), serializer.errors

    @pytest.mark.parametrize("campo", ["tipo", "nome", "email", "telefone"])
    def test_deve_invalidar_quando_campo_obrigatorio_ausente(
        self, responsavel_tecnico_payload_valido, campo
    ):
        """Deve invalidar quando um campo obrigatório não for informado."""
        payload = {**responsavel_tecnico_payload_valido}
        payload.pop(campo)
        serializer = ResponsavelTecnicoSerializer(data=payload)

        assert not serializer.is_valid()
        assert campo in serializer.errors
