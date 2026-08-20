"""Serializers do app escola."""

from rest_framework import serializers

from apps.escola.models import DiretoriaRegional, TipoEscola


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


class DiretoriaRegionalSerializer(serializers.ModelSerializer):
    """Serializa e valida os dados dos tipos de escola."""

    class Meta:
        model = DiretoriaRegional
        fields = (
            "id",
            "codigo",
            "nome",
            "abreviacao",
        )
