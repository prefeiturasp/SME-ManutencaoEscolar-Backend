"""Serializers utilizados nas operações de arquivos e anexos."""

from rest_framework import serializers


class ArquivoResponseSerializer(serializers.Serializer):
    """Serializa os dados de um arquivo retornados pela API.

    Define a estrutura utilizada nas respostas que representam arquivos
    armazenados, incluindo seus metadados e a URL para acesso ao conteúdo.
    """

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
    """Valida os dados necessários para realizar o upload de um arquivo.

    Recebe o arquivo que será encaminhado à camada de serviço para validação,
    preparação e armazenamento.
    """

    arquivo = serializers.FileField(
        help_text="Arquivo que será enviado para armazenamento.", required=True
    )
