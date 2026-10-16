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
    registro_funcional_criador: serializers.CharField = serializers.CharField(
        source="criado_por.username",
        read_only=True,
    )
    registro_funcional_editor: serializers.CharField = serializers.CharField(
        source="atualizado_por.username",
        read_only=True,
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
            "registro_funcional_criador",
            "registro_funcional_editor",
            "funcoes",
        )


class ProfissionalListSerializer(serializers.ModelSerializer):
    """Serializa um profissional para listagem."""

    funcoes = serializers.SerializerMethodField()

    def get_funcoes(self, profissional: Profissional) -> list[dict[str, str]]:
        """Retorna os nomes dos cargos exercidos pelo profissional.

        Args:
            profissional: Profissional que está sendo serializado.

        Returns:
            Nomes dos cargos vinculados ao profissional.
        """
        return [
            {"nome": funcao.cargo.nome, "uuid": str(funcao.uuid)}
            for funcao in profissional.funcoes.all()
        ]

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
        # A duplicidade de CPF/RG é validada no service, que devolve título e
        # mensagem conforme o que está duplicado (CPF, RG ou ambos).
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
