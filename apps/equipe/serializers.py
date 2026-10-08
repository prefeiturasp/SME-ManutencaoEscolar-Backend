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
        """Valida o vínculo entre o profissional e a função informados.

        Args:
            attrs: Dados do vínculo, contendo o profissional e a função que
                ele exercerá na equipe.

        Returns:
            Dados do vínculo validados.

        Raises:
            serializers.ValidationError: Se a função informada não estiver
                vinculada ao profissional selecionado.
        """
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
        """Valida se o nome da equipe possui caracteres não brancos.

        Args:
            value: Nome informado para a equipe.

        Returns:
            Nome validado, preservando o valor originalmente informado.

        Raises:
            serializers.ValidationError: Se o nome for formado apenas por
                espaços em branco.
        """
        if not value.strip():
            raise serializers.ValidationError("Este campo não pode ser vazio.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida se a empresa informada está associada ao lote.

        Args:
            attrs: Dados da equipe, contendo empresa e lote.

        Returns:
            Dados validados da equipe.

        Raises:
            serializers.ValidationError: Se o lote pertencer a outra empresa.
        """
        if attrs["empresa"].pk != attrs["lote"].empresa_id:
            raise serializers.ValidationError(
                {"empresa": EquipeErrorMessages.EMPRESA_LOTE_INVALIDA}
            )
        return attrs

    def validate_profissionais(
        self, value: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Valida os profissionais que compõem a equipe.

        Args:
            value: Lista de vínculos entre profissionais e suas respectivas
                funções na equipe.

        Returns:
            Lista de vínculos profissionais validada.

        Raises:
            serializers.ValidationError: Se nenhum profissional for informado
                ou se um mesmo profissional aparecer mais de uma vez.
        """
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


class LoteEquipeSerializer(serializers.ModelSerializer):
    """Serializa os dados do lote exibidos em uma equipe."""

    class Meta:
        """Configura os campos resumidos do lote."""

        model = Lote
        fields = ("nome", "periodo_inicial", "periodo_final")
        read_only_fields = fields


class EquipeListSerializer(serializers.ModelSerializer):
    """Serializa os dados resumidos de uma equipe."""

    nome_empresa = serializers.CharField(source="empresa.nome", read_only=True)
    lote = LoteEquipeSerializer(read_only=True)

    class Meta:
        """Configura os campos usados na serialização da equipe."""

        model = Equipe
        fields = (
            "nome",
            "nome_empresa",
            "lote",
            "situacao",
        )
