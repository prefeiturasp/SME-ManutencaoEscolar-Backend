"""Serializers do app escola."""

from rest_framework import serializers

from apps.escola.models import DiretoriaRegional, TipoEscola
from apps.escola.models.subprefeitura import Subprefeitura
from apps.escola.models.unidade_educacional import (
    DadosUnidadeEducacional,
    Unidadeeducacional,
)


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

    diretoria_regional = DiretoriaRegionalSerializer(read_only=True)

    class Meta:
        model = Subprefeitura
        fields = ("id", "uuid", "codigo_eol", "nome", "diretoria_regional")


class LoteUnidadeEducacionalSerializer(serializers.Serializer):
    """Serializa os dados do lote associado à unidade educacional."""

    id = serializers.IntegerField()
    uuid = serializers.UUIDField()
    codigo_cadastro = serializers.CharField()
    nome = serializers.CharField()
    status = serializers.BooleanField()


class DadosUnidadeEducacionalSerializer(serializers.ModelSerializer):
    """Serializa os dados de contato e endereço da unidade educacional."""

    class Meta:
        model = DadosUnidadeEducacional
        fields = (
            "email",
            "telefone",
            "logradouro",
            "numero",
            "bairro",
            "cep",
            "municipio",
            "uf",
        )


class UnidadeEducacionalSerializer(serializers.ModelSerializer):
    """Serializa os dados das unidades educacionais e seus relacionamentos."""

    diretoria_regional = DiretoriaRegionalSerializer(read_only=True)
    tipo_escola = TipoEscolaSerializer(read_only=True)
    subprefeitura = SubprefeituraSerializer(read_only=True)

    lote = serializers.SerializerMethodField()
    dados = DadosUnidadeEducacionalSerializer(read_only=True)

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
            "dados",
        )

    def get_lote(
        self,
        obj: Unidadeeducacional,
    ) -> dict | None:
        """Retorna o lote associado à diretoria regional da unidade."""
        lote_diretoria = obj.diretoria_regional.vinculo_lote.filter(
            lote__status=True
        ).first()

        if not lote_diretoria:
            return None

        lote = getattr(
            lote_diretoria,
            "lote",
            None,
        )

        if lote is None:
            return None

        return LoteUnidadeEducacionalSerializer(lote).data
