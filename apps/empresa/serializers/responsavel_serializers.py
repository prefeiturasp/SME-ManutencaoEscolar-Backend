"""Serializers da aplicação Empresa."""

from typing import Any

from rest_framework import serializers

from apps.core.exceptions import TelefoneInvalidoError
from apps.core.validacoes import validar_telefone
from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.models import ResponsavelTecnico
from apps.empresa.serializers.anexo_serializers import (
    AnexoResponsavelTecnicoSerializer,
)
from apps.usuarios.models import Usuario


class ResponsavelTecnicoSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de responsáveis técnicos."""

    uuid: serializers.UUIDField = serializers.UUIDField(required=False)
    criado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    atualizado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    atualizado_em: serializers.DateTimeField = serializers.DateTimeField(
        read_only=True
    )
    criado_em: serializers.DateTimeField = serializers.DateTimeField(
        read_only=True
    )
    arquivos: AnexoResponsavelTecnicoSerializer = (
        AnexoResponsavelTecnicoSerializer(
            many=True,
            required=False,
            source="anexos",
        )
    )

    class Meta:
        """Configuração do serializer de Responsavel Técnico."""

        model = ResponsavelTecnico
        fields = (
            "uuid",
            "tipo",
            "nome",
            "email",
            "numero_crea",
            "telefone",
            "numero_art",
            "arquivos",
            "criado_por",
            "criado_em",
            "atualizado_por",
            "atualizado_em",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida regras específicas do responsável técnico."""
        tipo = attrs.get("tipo")
        anexos = attrs.get("anexos")

        exige_anexo = tipo in {
            "engenheiro_civil",
            "engenheiro_eletricista",
        }
        if exige_anexo and not anexos:
            raise serializers.ValidationError(
                {
                    "arquivos": [
                        EmpresaErrorMessages.RESPONSAVEL_TECNICO_ANEXOS_OBRIGATORIOS
                    ]
                }
            )

        return attrs

    def validate_telefone(self, value: str) -> str:
        """Garante que o telefone tenha 10 ou 11 dígitos numéricos."""
        try:
            validar_telefone(value)
        except TelefoneInvalidoError:
            raise serializers.ValidationError(
                EmpresaErrorMessages.TELEFONE_INVALIDO
            ) from None
        return value
