"""Serializers da aplicação Serviço."""

from rest_framework import serializers

from apps.servico.constants import ServicoErrorMessages
from apps.servico.models import Servico


class ServicoSerializer(serializers.ModelSerializer):
    """Serializa o serviço para listagem e detalhes."""

    class Meta:
        """Configuração do serializer de serviço."""

        model = Servico
        fields = (
            "id",
            "uuid",
            "nome",
            "status",
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
        """Garante que o nome do serviço não seja vazio."""
        nome = value.strip()

        if not nome:
            raise serializers.ValidationError(
                ServicoErrorMessages.NOME_OBRIGATORIO
            )

        return nome
