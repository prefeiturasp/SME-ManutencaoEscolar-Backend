"""Serializers do app lote."""

from typing import Any

from django.db.models import query
from rest_framework import serializers

from apps.empresa.models import Empresa
from apps.empresa.serializers import EmpresaRelatedField, EmpresaSerializer
from apps.escola.models import DiretoriaRegional
from apps.escola.serializers import DiretoriaRegionalRelatedField, DiretoriaRegionalSerializer
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
    dres = serializers.SerializerMethodField()

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
            "dres",
            "criado_por",
            "criado_por_nome",
            "criado_em",
            "atualizado_por",
            "atualizado_por_nome",
            "username",
            "atualizado_em",
        )
        read_only_fields = fields

    def get_dres(self, obj):
        """Retorna as DREs vinculadas ao lote."""
        return DiretoriaRegionalSerializer(
            obj.dres,
            many=True,
        ).data


class LoteCriarSerializer(serializers.ModelSerializer):
    """Valida os dados necessários para cadastrar um lote."""

    dres = DiretoriaRegionalRelatedField(
        queryset=DiretoriaRegional.objects.all(),
        many=True,
        allow_empty=False,
    )

    empresa = EmpresaRelatedField(
        queryset=Empresa.objects.all()
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
            "dres",
        )

    def validate_dres(
        self,
        dres: list[DiretoriaRegional],
    ) -> list[DiretoriaRegional]:
        """Valida se não existem DREs repetidas na requisição."""
        dre_ids = [dre.pk for dre in dres]

        if len(dre_ids) != len(set(dre_ids)):
            raise serializers.ValidationError(
                "Não é permitido informar a mesma DRE mais de uma vez."
            )

        return dres

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
