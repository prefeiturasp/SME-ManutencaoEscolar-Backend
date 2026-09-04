"""_summary_."""

from rest_framework import serializers

from apps.escola.models.subprefeitura import Subprefeitura


class SubprefeituraSerializer(serializers.ModelSerializer):
    """Serializa e valida os dados das subprefeituras."""

    # diretoria_regional = DiretoriaRegionalSerializer(read_only=True)

    class Meta:
        model = Subprefeitura
        fields = ("id", "uuid", "codigo_eol", "nome")
        # "diretoria_regional")
