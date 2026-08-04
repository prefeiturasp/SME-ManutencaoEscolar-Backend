"""Schemas para a API de Fornecedor."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.fornecedor.serializers import (
    FornecedorCriarSerializer,
    FornecedorSerializer,
)

_FORNECEDOR_EXEMPLO_ENTRADA = {
    "nome": "Fornecedor Exemplo",
    "cnpj": "12345678000195",
    "status": True,
    "razao_social": "Fornecedor Exemplo LTDA",
    "link_rastreio": "https://www.exemplo.com/rastreio",
    "cep": "12345678",
    "logradouro": "Rua Exemplo",
    "numero": "123",
    "complemento": "Apto 101",
    "cidade": "Cidade Exemplo",
    "estado": "SP",
}

_FORNECEDOR_EXEMPLO_SAIDA = {
    "id": 1,
    "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    **_FORNECEDOR_EXEMPLO_ENTRADA,
}

FORNECEDOR_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=["Fornecedor"],
        summary="Lista os fornecedores",
        description="Retorna a lista de fornecedores cadastrados no sistema.",
        operation_id="listarFornecedores",
        parameters=[
            OpenApiParameter(
                name="nome",
                type=str,
                description=(
                    "Filtra fornecedores cujo nome contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="razao_social",
                type=str,
                description=(
                    "Filtra fornecedores cuja razão social contenha o "
                    "valor informado."
                ),
            ),
            OpenApiParameter(
                name="cnpj",
                type=str,
                description=(
                    "Filtra fornecedores cujo CNPJ contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="status",
                type=bool,
                description="Filtra fornecedores pelo status (ativo/inativo).",
            ),
        ],
        responses={
            200: FornecedorSerializer(many=True),
            401: OpenApiResponse(description="Credenciais inválidas"),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Lista de fornecedores",
                response_only=True,
                value=[_FORNECEDOR_EXEMPLO_SAIDA],
            ),
        ],
    ),
    create=extend_schema(
        tags=["Fornecedor"],
        summary="Cria um novo fornecedor",
        description="Adiciona um novo fornecedor ao sistema.",
        operation_id="cadastrarFornecedor",
        request=FornecedorCriarSerializer,
        responses={
            201: OpenApiResponse(description="Fornecedor criado com sucesso"),
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description="Credenciais inválidas"),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de cadastro de fornecedor",
                request_only=True,
                value=_FORNECEDOR_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Fornecedor cadastrado com sucesso",
                response_only=True,
                value=_FORNECEDOR_EXEMPLO_SAIDA,
            ),
        ],
    ),
)
