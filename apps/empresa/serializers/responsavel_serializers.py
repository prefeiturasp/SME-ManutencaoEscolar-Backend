"""Serializers da aplicação Empresa."""

from rest_framework import serializers

from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.models import Empresa, ResponsavelTecnico
from apps.usuarios.models import Usuario


class ResponsavelTecnicoSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de responsáveis técnicos."""

    empresa: serializers.SlugRelatedField[Empresa] = (
        serializers.SlugRelatedField(
            slug_field="uuid", queryset=Empresa.objects.all()
        )
    )
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
            "tipo",
            "nome",
            "empresa",
            "email",
            "numero_crea",
            "telefone",
            "numero_art",
            "criado_por",
            "criado_em",
            "atualizado_por",
            "atualizado_em",
        )

    def validate_empresa(self, value: Empresa) -> Empresa:
        """Garante que a empresa exista e seja válida."""
        if not value:
            raise serializers.ValidationError(
                EmpresaErrorMessages.EMPRESA_INVALIDA
            )
        return value
