"""Schemas para a API de Serviço."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

SERVICO_SCHEMA = extend_schema_view(
    create=extend_schema(
        tags=["Serviço"],
        summary="Cria um novo serviço",
        description="Adiciona um novo serviço ao sistema.",
        responses={
            201: OpenApiResponse(
                description="Serviço criado com sucesso",
                examples=[
                    OpenApiExample(
                        "Sucesso",
                        value={
                            "id": "uuid",
                            "nome": "Pintura",
                            "status": True,
                        },
                    ),
                ],
            ),
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description="Credenciais inválidas"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
    ),
)