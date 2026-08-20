"""Serializers do app lote."""

from typing import Any

from rest_framework import serializers

from apps.empresa.models import Empresa
from apps.empresa.serializers import EmpresaSerializer
from apps.escola.models import DiretoriaRegional
from apps.escola.serializers import (
    DiretoriaRegionalSerializer,
)
from apps.lote.models import Lote


class LoteSerializer(serializers.ModelSerializer):
    """Serializa os dados de um lote."""

    criado_por_nome = serializers.CharField(
        source="criado_por.nome",
        read_only=True,
        allow_null=True,
    )
    atualizado_por_nome = serializers.CharField(
        source="atualizado_por.nome",
        read_only=True,
        allow_null=True,
    )
    username = serializers.CharField(
        source="criado_por.username",
        read_only=True,
        allow_null=True,
    )
    diretorias_regionais = serializers.SerializerMethodField()

    empresa = EmpresaSerializer()

    class Meta:
        """Configura o serializer de lote."""

        model = Lote
        fields = (
            "id",
            "uuid",
            "codigo_cadastro",
            "nome",
            "status",
            "empresa",
            "periodo_inicial",
            "periodo_final",
            "diretorias_regionais",
            "criado_por",
            "criado_por_nome",
            "criado_em",
            "atualizado_por",
            "atualizado_por_nome",
            "username",
            "atualizado_em",
        )
        read_only_fields = fields

    def get_diretorias_regionais(
        self,
        obj: Lote,
    ) -> list[dict[str, Any]]:
        """Retorna as diretorias regionais vinculadas ao lote."""
        return list(
            DiretoriaRegionalSerializer(
                obj.diretorias_regionais,
                many=True,
            ).data
        )


class LoteCriarSerializer(serializers.ModelSerializer):
    """Valida os dados necessários para cadastrar um lote."""

    diretorias_regionais = serializers.SlugRelatedField(
        slug_field="id",
        queryset=DiretoriaRegional.objects.all(),
        many=True,
    )

    empresa = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Empresa.objects.all(),
    )

    class Meta:
        """Configura o serializer de criação de lotes."""

        model = Lote
        fields = (
            "nome",
            "codigo_cadastro",
            "empresa",
            "periodo_inicial",
            "periodo_final",
            "status",
            "diretorias_regionais",
        )

    def validate_diretorias_regionais(
        self,
        diretorias_regionais: list[DiretoriaRegional],
    ) -> list[DiretoriaRegional]:
        """Valida se existem diretorias regionais repetidas."""
        diretoria_regional_ids = [
            diretoria_regional.pk
            for diretoria_regional in diretorias_regionais
        ]

        if len(diretoria_regional_ids) != len(set(diretoria_regional_ids)):
            raise serializers.ValidationError(
                """Não é permitido informar a mesma
                    diretoria_regional mais de uma vez."""
            )

        return diretorias_regionais

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida o período inicial e final do lote."""
        periodo_inicial = attrs.get("periodo_inicial")
        periodo_final = attrs.get("periodo_final")

        if (
            periodo_inicial is not None
            and periodo_final is not None
            and periodo_final < periodo_inicial
        ):
            raise serializers.ValidationError(
                {
                    "periodo_final": (
                        "O período final não pode ser anterior "
                        "ao período inicial."
                    )
                }
            )

        return attrs
