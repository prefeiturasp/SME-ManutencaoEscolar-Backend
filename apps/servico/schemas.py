"""Schemas para a API de Serviço."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.servico.serializers import ServicoCriarSerializer

SERVICO_SCHEMA = extend_schema_view(
    create=extend_schema(
        tags=["Serviço"],
        summary="Cria um novo serviço",
        description="Adiciona um novo serviço ao sistema.",
        request=ServicoCriarSerializer,
        responses={
            201: ServicoCriarSerializer,
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description="Credenciais inválidas"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de Serviço",
                value={"nome": "Pintar", "status": True},
            ),
            OpenApiExample(
                name="Serviço criado com sucesso",
                response_only=True,
                status_codes=["201"],
                value={
                    "id": 1,
                    "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
                    "nome": "Pintura",
                    "status": True,
                },
            ),
        ],
    ),
)
