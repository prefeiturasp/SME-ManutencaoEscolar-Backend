"""Serializers do app escola."""

from rest_framework import serializers

from apps.escola.models import DiretoriaRegional, TipoEscola
from apps.escola.models.subprefeitura import Subprefeitura
from apps.escola.models.unidade_educacional import Unidadeeducacional


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
            "nome_curto",
        )


class SubprefeituraSerializer(serializers.ModelSerializer):
    """Serializa e valida os dados das subprefeituras."""

    class Meta:
        model = Subprefeitura
        fields = (
            "id",
            "uuid",
            "codigo_eol",
            "nome",
        )


class LoteUnidadeEducacionalSerializer(serializers.Serializer):
    """Serializa os dados do lote associado à unidade educacional."""

    id = serializers.IntegerField()
    uuid = serializers.UUIDField()
    codigo_cadastro = serializers.CharField()
    nome = serializers.CharField()
    status = serializers.BooleanField()


class UnidadeEducacionalSerializer(serializers.ModelSerializer):
    """Serializa os dados das unidades educacionais e seus relacionamentos."""

    diretoria_regional = DiretoriaRegionalSerializer(read_only=True)
    tipo_escola = TipoEscolaSerializer(read_only=True)
    subprefeitura = SubprefeituraSerializer(read_only=True)

    lote = serializers.SerializerMethodField()

    class Meta:
        model = Unidadeeducacional
        fields = (
            "id",
            "uuid",
            "codigo_eol",
            "nome",
            "diretoria_regional",
            "tipo_escola",
            "subprefeitura",
            "lote",
            "status",
        )

    def get_lote(
        self,
        obj: Unidadeeducacional,
    ) -> dict | None:
        """Retorna o lote associado à diretoria regional da unidade."""
        vinculo = getattr(
            obj.diretoria_regional,
            "vinculo_lote",
            None,
        )

        if vinculo is None:
            return None

        lote = vinculo.lote

        return LoteUnidadeEducacionalSerializer(lote).data
