"""Serializers do app cargo."""

from typing import Any

from rest_framework import serializers

from apps.cargo.models import Cargo, DocumentoCargo


class DocumentoCargoCriarSerializer(serializers.ModelSerializer):
    """Valida os dados de um documento do cargo."""

    class Meta:
        """Configura o serializer de criação do documento."""

        model = DocumentoCargo
        fields = ("nome",)


class CargoCriarSerializer(serializers.ModelSerializer):
    """Valida os dados necessários para cadastrar um cargo."""

    documentos = DocumentoCargoCriarSerializer(
        many=True,
        required=False,
    )

    class Meta:
        """Configura o serializer de criação de cargo."""

        model = Cargo
        fields = (
            "nome",
            "exige_documento",
            "status",
            "documentos",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida a relação entre o cargo e seus documentos.

        Args:
            attrs: Dados recebidos para criação do cargo.

        Returns:
            Dados validados para criação do cargo.

        Raises:
            serializers.ValidationError: Se os documentos informados forem
                incompatíveis com a configuração do cargo.
        """
        exige_documento = attrs.get("exige_documento", False)
        documentos = attrs.get("documentos", [])

        if exige_documento and not documentos:
            raise serializers.ValidationError(
                {
                    "documentos": (
                        "Informe ao menos um documento para este cargo."
                    ),
                }
            )

        if not exige_documento and documentos:
            raise serializers.ValidationError(
                {
                    "documentos": (
                        "Um cargo que não exige documentos não pode possuir "
                        "documentos vinculados."
                    ),
                }
            )

        return attrs
