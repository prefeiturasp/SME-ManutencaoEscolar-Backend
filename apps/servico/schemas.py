"""Schemas para a API de Serviço."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.servico.serializers import (
    ServicoCriarSerializer,
    ServicoSerializer,
)

_SERVICO_EXEMPLO_ENTRADA = {
    "nome": "Pintura",
    "status": True,
}

_SERVICO_EXEMPLO_SAIDA = {
    "id": 1,
    "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    **_SERVICO_EXEMPLO_ENTRADA,
}

SERVICO_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=["Serviço"],
        summary="Lista os serviços",
        description="Retorna a lista de serviços cadastrados no sistema.",
        operation_id="listarServicos",
        parameters=[
            OpenApiParameter(
                name="nome",
                type=str,
                description=(
                    "Filtra serviços cujo nome contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="status",
                type=bool,
                description="Filtra serviços pelo status (ativo/inativo).",
            ),
        ],
        responses={
            200: ServicoSerializer(many=True),
            401: OpenApiResponse(description="Credenciais inválidas"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Lista de serviços",
                response_only=True,
                value=[_SERVICO_EXEMPLO_SAIDA],
            ),
        ],
    ),
    retrieve=extend_schema(exclude=True),
    create=extend_schema(
        tags=["Serviço"],
        summary="Cria um novo serviço",
        description="Adiciona um novo serviço ao sistema.",
        operation_id="cadastrarServico",
        request=ServicoCriarSerializer,
        responses={
            201: ServicoSerializer,
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description="Credenciais inválidas"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de cadastro de serviço",
                request_only=True,
                value=_SERVICO_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Serviço cadastrado com sucesso",
                response_only=True,
                value=_SERVICO_EXEMPLO_SAIDA,
            ),
        ],
    ),
)
