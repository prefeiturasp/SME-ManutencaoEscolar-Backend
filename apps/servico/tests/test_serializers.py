"""Serializers da aplicação Serviço."""

from rest_framework import serializers

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
                    "blank": "O nome do serviço é obrigatório.",
                }
            }
        }

    def validate_nome(self, value: str) -> str:
        """Garante que o nome do serviço não seja vazio."""
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "O nome do serviço é obrigatório."
            )

        return value
