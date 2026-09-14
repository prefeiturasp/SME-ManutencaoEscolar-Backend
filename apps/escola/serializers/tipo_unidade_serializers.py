"""Serializers de Tipo de Escola."""

from rest_framework import serializers

from apps.escola.models import TipoEscola


class TipoEscolaSerializer(serializers.ModelSerializer):
    """Serializa e valida os dados dos tipos de escola."""

    class Meta:
        model = TipoEscola
        fields = (
            "id",
            "uuid",
            "codigo_eol",
            "sigla",
        )
