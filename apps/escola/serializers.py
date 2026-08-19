"""Serializers do app escola."""

from typing import Any

from rest_framework import serializers

from apps.escola.models import TipoEscola, DiretoriaRegional

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

class DiretoriaRegionalRelatedField(
    serializers.PrimaryKeyRelatedField
):
    """Recebe o ID da DRE e retorna seus dados completos."""

    def to_representation(
        self,
        value: DiretoriaRegional,
    ) -> dict[str, Any]:
        """Serializa os dados completos da DRE."""
        return DiretoriaRegionalSerializer(
            value,
            context=self.context,
        ).data
