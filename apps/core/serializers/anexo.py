"""Serializers de Anexo."""

from rest_framework import serializers


class ArquivoResponseSerializer(serializers.Serializer):
    """Representa os dados de um arquivo retornados pela API."""

    uuid = serializers.UUIDField(
        help_text="Identificador único do arquivo.",
    )
    nome = serializers.CharField(
        help_text="Nome original do arquivo.",
    )
    tipo = serializers.CharField(
        help_text="Tipo do arquivo conforme as categorias da aplicação.",
    )
    tipo_mime = serializers.CharField(
        help_text="Tipo MIME do arquivo.",
    )
    tamanho = serializers.IntegerField(
        help_text="Tamanho do arquivo em bytes.",
    )
    url = serializers.URLField(
        help_text="URL para acesso ao arquivo armazenado.",
    )


class ArquivoUploadSerializer(serializers.Serializer):
    """Representa os dados necessários para realizar o upload de um arquivo."""

    arquivo = serializers.FileField(
        help_text="Arquivo que será enviado para armazenamento.", required=True
    )
