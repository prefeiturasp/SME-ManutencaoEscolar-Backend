"""Serializers da aplicação Empresa."""

from rest_framework import serializers

from apps.empresa.models import ResponsavelTecnico
from apps.usuarios.models import Usuario


class ResponsavelTecnicoSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de responsáveis técnicos."""

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
            "email",
            "numero_crea",
            "telefone",
            "numero_art",
            "criado_por",
            "criado_em",
            "atualizado_por",
            "atualizado_em",
        )
