"""Schemas para a API de Empresa."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.empresa.serializers import (
    EmpresaCriarSerializer,
    EmpresaSerializer,
)

_EMPRESA_EXEMPLO_ENTRADA = {
    "nome": "Empresa Exemplo",
    "cnpj": "12345678000195",
    "status": True,
    "razao_social": "Empresa Exemplo LTDA",
    "link_rastreio": "https://www.exemplo.com/rastreio",
    "cep": "12345678",
    "logradouro": "Rua Exemplo",
    "numero": "123",
    "complemento": "Apto 101",
    "cidade": "Cidade Exemplo",
    "estado": "SP",
}

_EMPRESA_EXEMPLO_SAIDA = {
    "id": 1,
    "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    **_EMPRESA_EXEMPLO_ENTRADA,
}

EMPRESA_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=["Empresa"],
        summary="Lista as empresas",
        description="Retorna a lista de empresas cadastradas no sistema.",
        operation_id="listarEmpresas",
        parameters=[
            OpenApiParameter(
                name="nome",
                type=str,
                description=(
                    "Filtra empresas cujo nome contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="razao_social",
                type=str,
                description=(
                    "Filtra empresas cuja razão social contenha o "
                    "valor informado."
                ),
            ),
            OpenApiParameter(
                name="cnpj",
                type=str,
                description=(
                    "Filtra empresas cujo CNPJ contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="status",
                type=bool,
                description="Filtra empresas pelo status (ativo/inativo).",
            ),
        ],
        responses={
            200: EmpresaSerializer(many=True),
            401: OpenApiResponse(description="Credenciais inválidas"),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Lista de empresas",
                response_only=True,
                value=[_EMPRESA_EXEMPLO_SAIDA],
            ),
        ],
    ),
    retrieve=extend_schema(exclude=True),
    create=extend_schema(
        tags=["Empresa"],
        summary="Cria uma nova empresa",
        description="Adiciona uma nova empresa ao sistema.",
        operation_id="cadastrarEmpresa",
        request=EmpresaCriarSerializer,
        responses={
            201: OpenApiResponse(description="Empresa criada com sucesso"),
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description="Credenciais inválidas"),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de cadastro de empresa",
                request_only=True,
                value=_EMPRESA_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Empresa criada com sucesso",
                response_only=True,
                value=_EMPRESA_EXEMPLO_SAIDA,
            ),
        ],
    ),
)
