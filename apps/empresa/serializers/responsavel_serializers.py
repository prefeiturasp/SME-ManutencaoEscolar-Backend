"""Serializers da aplicação Empresa."""

from rest_framework import serializers

from apps.core.exceptions import TelefoneInvalidoError
from apps.core.validacoes import validar_telefone
from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.models import ResponsavelTecnico
from apps.usuarios.models import Usuario


class ResponsavelTecnicoSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de responsáveis técnicos."""

    uuid: serializers.UUIDField = serializers.UUIDField(required=False)
    criado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    atualizado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    atualizado_em: serializers.DateTimeField = serializers.DateTimeField(
        read_only=True
    )
    criado_em: serializers.DateTimeField = serializers.DateTimeField(
        read_only=True
    )

    class Meta:
        """Configuração do serializer de Responsavel Técnico."""

        model = ResponsavelTecnico
        fields = (
            "uuid",
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
        )

    def validate_telefone(self, value: str) -> str:
        """Garante que o telefone tenha 10 ou 11 dígitos numéricos."""
        try:
            validar_telefone(value)
        except TelefoneInvalidoError:
            raise serializers.ValidationError(
                EmpresaErrorMessages.TELEFONE_INVALIDO
            ) from None
        return value
