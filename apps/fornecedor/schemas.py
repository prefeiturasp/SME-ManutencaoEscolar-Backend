"""Schemas para a API de Fornecedor."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

FORNECEDOR_SCHEMA = extend_schema_view(
    create=extend_schema(
        tags=["Fornecedor"],
        summary="Cria um novo fornecedor",
        description="Adiciona um novo fornecedor ao sistema.",
        responses={
            201: OpenApiResponse(
                description="Fornecedor criado com sucesso",
                examples=[
                    OpenApiExample(
                        "Sucesso",
                        value={
                            "id": "uuid",
                            "nome": "Fornecedor Exemplo",
                            "cnpj": "12345678000195",
                            "status": "ativo",
                            "razao_social": "Fornecedor Exemplo LTDA",
                            "link_rastreio": "https://www.exemplo.com/rastreio",
                            "cep": "12345678",
                            "logradouro": "Rua Exemplo",
                            "numero": "123",
                            "complemento": "Apto 101",
                            "cidade": "Cidade Exemplo",
                            "estado": "SP",
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
