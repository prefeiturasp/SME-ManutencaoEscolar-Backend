"""Serializers dos anexos de responsáveis técnicos."""

from typing import Any, cast

from django.core.files.uploadedfile import UploadedFile
from django.core.validators import FileExtensionValidator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.constants import MAPA_EXTENSOES_TIPO_ARQUIVO
from apps.empresa.models import AnexoResponsavelTecnico
from apps.usuarios.models import Usuario


@extend_schema_field(OpenApiTypes.BINARY)
class ArquivoUploadField(serializers.FileField):
    """Representa um arquivo enviado como conteúdo binário no OpenAPI."""


class AnexoResponsavelTecnicoSerializer(serializers.ModelSerializer):
    """Serializa os arquivos associados a um responsável técnico."""

    uuid = serializers.UUIDField(required=False)
    arquivo = ArquivoUploadField(
        write_only=True,
        required=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=MAPA_EXTENSOES_TIPO_ARQUIVO
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
