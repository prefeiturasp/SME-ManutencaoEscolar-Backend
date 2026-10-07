"""Serializers do domínio Equipe."""

from typing import Any

from rest_framework import serializers

from apps.empresa.models import Empresa
from apps.equipe.constants import EquipeErrorMessages
from apps.equipe.models import Equipe, ProfissionalEquipe
from apps.lote.models import Lote
from apps.profissional.models import FuncaoProfissional, Profissional


class ProfissionalEquipeSerializer(serializers.ModelSerializer):
    """Serializa um profissional e sua função na equipe."""

    profissional = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Profissional.objects.all(),
    )
    funcao = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=FuncaoProfissional.objects.all(),
    )
    cpf = serializers.CharField(source="profissional.cpf", read_only=True)
    nome = serializers.CharField(source="profissional.nome", read_only=True)
    nome_funcao = serializers.CharField(
        source="funcao.cargo.nome", read_only=True
    )

    class Meta:
        """Configura os campos do vínculo profissional-equipe."""

        model = ProfissionalEquipe
        fields = (
            "profissional",
            "cpf",
            "nome",
            "funcao",
            "nome_funcao",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida se a função pertence ao profissional selecionado."""
        if attrs["funcao"].profissional_id != attrs["profissional"].pk:
            raise serializers.ValidationError(
                {"funcao": EquipeErrorMessages.FUNCAO_INVALIDA}
            )
        return attrs


class EquipeCriarSerializer(serializers.ModelSerializer):
    """Valida e serializa o cadastro de uma equipe."""

    empresa = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Empresa.objects.all()
    )
    lote = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Lote.objects.all()
    )
    profissionais = ProfissionalEquipeSerializer(many=True)

    class Meta:
        """Configura os campos usados na criação de equipe."""

        model = Equipe
        fields = (
            "uuid",
            "nome",
            "situacao",
            "empresa",
            "lote",
            "profissionais",
        )
        read_only_fields = ("uuid",)

    def validate_nome(self, value: str) -> str:
        """Rejeita nomes formados apenas por espaços."""
        if not value.strip():
            raise serializers.ValidationError("Este campo não pode ser vazio.")
        return value

    def validate_profissionais(
        self, value: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Exige ao menos um profissional e rejeita repetições."""
        if not value:
            raise serializers.ValidationError(
                EquipeErrorMessages.PROFISSIONAL_OBRIGATORIO
            )
        ids = [item["profissional"].pk for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                EquipeErrorMessages.PROFISSIONAL_DUPLICADO
            )
        return value
