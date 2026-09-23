"""Serializers do domínio Profissional."""

from typing import Any

from rest_framework import serializers

from apps.profissional.constants import ProfissionalErrorMessages
from apps.profissional.models import Profissional
from apps.profissional.serializers.funcao_serializers import (
    FuncaoProfissionalSerializer,
)
from apps.usuarios.models.usuario import Usuario


class ProfissionalSerializer(serializers.ModelSerializer):
    """Serializa um profissional para detalhes."""

    criado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    atualizado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    funcoes: FuncaoProfissionalSerializer = FuncaoProfissionalSerializer(
        many=True, read_only=True
    )

    class Meta:
        """Configuração do serializer de profissional."""

        model = Profissional
        fields = (
            "id",
            "uuid",
            "nome",
            "cpf",
            "rg",
            "status",
            "criado_por",
            "criado_em",
            "atualizado_por",
            "atualizado_em",
            "funcoes",
        )


class ProfissionalListSerializer(serializers.ModelSerializer):
    """Serializa um profissional para listagem."""

    funcoes = serializers.SerializerMethodField()

    def get_funcoes(self, profissional: Profissional) -> list[str]:
        """Retorna os nomes dos cargos exercidos pelo profissional.

        Args:
            profissional: Profissional que está sendo serializado.

        Returns:
            Nomes dos cargos vinculados ao profissional.
        """
        return [funcao.cargo.nome for funcao in profissional.funcoes.all()]

    class Meta:
        """Configuração do serializer de profissional."""

        model = Profissional
        fields = (
            "uuid",
            "nome",
            "cpf",
            "rg",
            "status",
            "funcoes",
        )


class ProfissionalCriarAtualizarSerializer(serializers.ModelSerializer):
    """Serializa o cadastro e atualização de profissionais."""

    funcoes: FuncaoProfissionalSerializer = FuncaoProfissionalSerializer(
        many=True
    )

    class Meta:
        """Configuração do serializer de profissional."""

        model = Profissional
        fields = (
            "nome",
            "cpf",
            "rg",
            "status",
            "funcoes",
        )
        extra_kwargs: dict[str, dict[str, Any]] = {
            "cpf": {"validators": []},
            "rg": {"validators": []},
        }

    def validate_funcoes(
        self, value: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Valida as funções informadas para o profissional.

        Args:
            value: Funções a serem validadas.

        Returns:
            As funções validadas.

        Raises:
            serializers.ValidationError: Se nenhuma função for informada ou
                se houver cargos duplicados.
        """
        if not value:
            raise serializers.ValidationError(
                ProfissionalErrorMessages.FUNCAO_PROFISSIONAL_OBRIGATORIA
            )
        cargos = [funcao["cargo"].pk for funcao in value]
        if len(cargos) != len(set(cargos)):
            raise serializers.ValidationError(
                ProfissionalErrorMessages.FUNCAO_PROFISSIONAL_DUPLICADA
            )
        return value

    def validate_cpf(self, value: str) -> str:
        """Valida se o CPF já está cadastrado para outro profissional.

        Args:
            value: CPF a ser validado.

        Returns:
            O CPF validado.

        Raises:
            serializers.ValidationError: Se o CPF já estiver cadastrado.
        """
        profissionais = Profissional.objects.filter(cpf=value)
        if self.instance is not None:
            profissionais = profissionais.exclude(pk=self.instance.pk)
        if profissionais.exists():
            raise serializers.ValidationError(
                ProfissionalErrorMessages.PROFISSIONAL_CPF_JA_CADASTRADO
            )
        return value

    def validate_rg(self, value: str) -> str:
        """Valida se o RG já está cadastrado para outro profissional.

        Args:
            value: RG a ser validado.

        Returns:
            O RG validado.

        Raises:
            serializers.ValidationError: Se o RG já estiver cadastrado.
        """
        profissionais = Profissional.objects.filter(rg=value)
        if self.instance is not None:
            profissionais = profissionais.exclude(pk=self.instance.pk)
        if profissionais.exists():
            raise serializers.ValidationError(
                ProfissionalErrorMessages.PROFISSIONAL_RG_JA_CADASTRADO
            )
        return value
