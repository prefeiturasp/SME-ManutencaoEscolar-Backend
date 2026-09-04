"""Serializers de Subprefeitura."""

from rest_framework import serializers

from apps.escola.models.subprefeitura import Subprefeitura


class SubprefeituraSerializer(serializers.ModelSerializer):
    """Serializa e valida os dados das subprefeituras."""

    class Meta:
        model = Subprefeitura
        fields = ("id", "uuid", "codigo_eol", "nome")
