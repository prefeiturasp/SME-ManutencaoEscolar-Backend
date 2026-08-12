"""Serializers da aplicação Serviço."""

from rest_framework import serializers

from apps.servico.constants import ServicoErrorMessages
from apps.servico.models import Servico


class ServicoSerializer(serializers.ModelSerializer):
    """Serializa o serviço para listagem e detalhes."""

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

    class Meta:
        """Configuração do serializer de serviço."""

        model = Servico
        fields = (
            "id",
            "uuid",
            "nome",
            "status",
            "criado_por",
            "criado_por_nome",
            "criado_em",
            "atualizado_por",
            "atualizado_por_nome",
            "atualizado_em",
        )
        read_only_fields = (
            "id",
            "uuid",
            "criado_por",
            "criado_por_nome",
            "criado_em",
            "atualizado_por",
            "atualizado_por_nome",
            "atualizado_em",
        )

class ServicoCriarSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de serviços."""

    class Meta:
        """Configuração do serializer de criação de serviço."""

        model = Servico
        fields = (
            "nome",
            "status",
        )
        extra_kwargs = {
            "nome": {
                "error_messages": {
                    "unique": ServicoErrorMessages.NOME_JA_CADASTRADO,
                    "blank": ServicoErrorMessages.NOME_OBRIGATORIO,
                },
            },
        }

    def validate_nome(self, value: str) -> str:
        """Remove espaços e impede nomes vazios."""
        nome = value.strip()

        if not nome:
            raise serializers.ValidationError(
                ServicoErrorMessages.NOME_OBRIGATORIO
            )

        return nome


class ServicoAtualizarSerializer(ServicoCriarSerializer):
    """Serializa a atualização parcial de serviços."""