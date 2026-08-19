"""Serializers da aplicação Empresa."""

from typing import Any

from rest_framework import serializers

from apps.core.exceptions import (
    CepInvalidoError,
    CnpjInvalidoError,
    LinkRastreioInvalidoError,
)
from apps.core.validacoes import (
    validar_formato_cep,
    validar_formato_cnpj,
    validar_formato_link_rastreio,
)
from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.models import Empresa
from apps.usuarios.models import Usuario


class EmpresaSerializer(serializers.ModelSerializer):
    """Serializa a empresa para listagem e detalhes."""

    criado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    atualizado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )

    class Meta:
        """Configuração do serializer de empresa."""

        model = Empresa
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
            "criado_por",
            "criado_em",
            "atualizado_por",
            "atualizado_em",
        )


class EmpresaCriarAtualizarSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de empresas."""

    class Meta:
        """Configuração do serializer de empresa."""

        model = Empresa
        fields = (
            "nome",
            "cnpj",
            "razao_social",
            "status",
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
                EmpresaErrorMessages.CNPJ_INVALIDO
            ) from None
        return value

    def validate_cep(self, value: str) -> str:
        """Garante que o CEP contenha apenas dígitos e tenha 8 caracteres."""
        try:
            validar_formato_cep(value)
        except CepInvalidoError:
            raise serializers.ValidationError(
                EmpresaErrorMessages.CEP_INVALIDO
            ) from None
        return value

    def validate_link_rastreio(self, value: str) -> str:
        """Garante que o link de rastreio seja uma URL válida."""
        if value:
            try:
                validar_formato_link_rastreio(value)
            except LinkRastreioInvalidoError:
                raise serializers.ValidationError(
                    EmpresaErrorMessages.LINK_RASTREIO_INVALIDO
                ) from None
        return value


class EmpresaRelatedField(
    serializers.PrimaryKeyRelatedField
):
    """Recebe o ID da Empresa e retorna seus dados completos."""

    def to_representation(
        self,
        value: Empresa,
    ) -> dict[str, Any]:
        """Serializa os dados completos da empresa."""
        return EmpresaSerializer(
            value,
            context=self.context,
        ).data
