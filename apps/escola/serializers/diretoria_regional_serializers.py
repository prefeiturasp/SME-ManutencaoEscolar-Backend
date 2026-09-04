"""_summary_."""

from rest_framework import serializers

from apps.escola.models import DiretoriaRegional


class DiretoriaRegionalSerializer(serializers.ModelSerializer):
    """Serializa e valida os dados dos tipos de escola."""

    class Meta:
        model = DiretoriaRegional
        fields = (
            "id",
            "codigo",
            "nome",
            "abreviacao",
            "nome_curto",
        )
