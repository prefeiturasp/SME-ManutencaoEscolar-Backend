"""Serializers da aplicação Fornecedor."""

from rest_framework import serializers

from apps.fornecedor.constants import FornecedorErrorMessages
from apps.fornecedor.models import Fornecedor
from apps.utils.validacoes import (
    CepInvalidoError,
    CnpjInvalidoError,
    LinkRastreioInvalidoError,
    validar_formato_cep,
    validar_formato_cnpj,
    validar_formato_link_rastreio,
)


class FornecedorSerializer(serializers.ModelSerializer):
    """Serializa o fornecedor para listagem e detalhes."""

    class Meta:
        """Configuração do serializer de fornecedor."""

        model = Fornecedor
        fields = (
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
        )


class FornecedorCriarSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de fornecedores."""

    class Meta:
        """Configuração do serializer de fornecedor."""

        model = Fornecedor
        fields = (
            "nome",
            "cnpj",
            "razao_social",
            "link_rastreio",
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "cidade",
            "estado",
        )

    def validate_cnpj(self, value: str) -> str:
        """Garante que o CNPJ contenha apenas dígitos e tenha 14 caracteres."""
        try:
            validar_formato_cnpj(value)
        except CnpjInvalidoError:
            raise serializers.ValidationError(
                FornecedorErrorMessages.CNPJ_INVALIDO
            ) from None
        return value

    def validate_cep(self, value: str) -> str:
        """Garante que o CEP contenha apenas dígitos e tenha 8 caracteres."""
        try:
            validar_formato_cep(value)
        except CepInvalidoError:
            raise serializers.ValidationError(
                FornecedorErrorMessages.CEP_INVALIDO
            ) from None
        return value

    def validate_link_rastreio(self, value: str) -> str:
        """Garante que o link de rastreio seja uma URL válida."""
        if value:
            try:
                validar_formato_link_rastreio(value)
            except LinkRastreioInvalidoError:
                raise serializers.ValidationError(
                    FornecedorErrorMessages.LINK_RASTREIO_INVALIDO
                ) from None
        return value
