"""Serializers dos anexos de responsáveis técnicos."""

from typing import Any, cast

from django.core.files.uploadedfile import UploadedFile
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from apps.empresa.models import AnexoResponsavelTecnico
from apps.usuarios.models import Usuario

EXTENSOES_ANEXO_RESPONSAVEL_TECNICO = ("pdf", "png", "jpeg", "jpg")


class AnexoResponsavelTecnicoSerializer(serializers.ModelSerializer):
    """Serializa os arquivos associados a um responsável técnico."""

    uuid = serializers.UUIDField(required=False)
    arquivo = serializers.FileField(
        write_only=True,
        required=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=EXTENSOES_ANEXO_RESPONSAVEL_TECNICO
            )
        ],
    )
    nome = serializers.CharField(source="nome_original", read_only=True)
    arquivo_url = serializers.URLField(source="url", read_only=True)
    anexado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(
            source="criado_por",
            slug_field="nome",
            read_only=True,
        )
    )
    anexado_em = serializers.DateTimeField(source="criado_em", read_only=True)

    class Meta:
        model = AnexoResponsavelTecnico
        fields = (
            "uuid",
            "nome",
            "arquivo_url",
            "arquivo",
            "anexado_por",
            "anexado_em",
        )
        read_only_fields = (
            "nome",
            "arquivo_url",
            "anexado_por",
            "anexado_em",
        )

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """Aceita tanto o arquivo puro quanto o objeto ``{"arquivo": ...}``."""
        if isinstance(data, UploadedFile):
            data = {"arquivo": data}
        return cast(dict[str, Any], super().to_internal_value(data))
