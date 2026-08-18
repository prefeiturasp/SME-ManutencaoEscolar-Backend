"""Schemas para a API de Empresa."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.empresa.serializers import (
    EmpresaCriarAtualizarSerializer,
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

_CREDENCIAL_INVALID_DESCRIPTION = "Credenciais inválidas"
_ERRO_SERVIDOR_DESCRIPTION = "Erro no servidor"
_EMPRESA_NAO_ENCONTRADA_DESCRIPTION = "Empresa não encontrada"

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
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
        examples=[
            OpenApiExample(
                name="Lista de empresas",
                response_only=True,
                value=[_EMPRESA_EXEMPLO_SAIDA],
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Empresa"],
        summary="Detalhes de uma empresa",
        description="Retorna os detalhes de uma empresa específica.",
        operation_id="detalharEmpresa",
        responses={
            200: EmpresaSerializer,
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            404: OpenApiResponse(
                description=_EMPRESA_NAO_ENCONTRADA_DESCRIPTION
            ),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
        examples=[
            OpenApiExample(
                name="Detalhes da empresa",
                response_only=True,
                value=_EMPRESA_EXEMPLO_SAIDA,
            ),
        ],
    ),
    create=extend_schema(
        tags=["Empresa"],
        summary="Cria uma nova empresa",
        description="Adiciona uma nova empresa ao sistema.",
        operation_id="cadastrarEmpresa",
        request=EmpresaCriarAtualizarSerializer,
        responses={
            201: OpenApiResponse(description="Empresa criada com sucesso"),
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
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
    update=extend_schema(
        tags=["Empresa"],
        summary="Atualiza uma empresa",
        description=(
            "Atualiza integralmente os dados de uma empresa existente."
        ),
        operation_id="atualizarEmpresa",
        request=EmpresaCriarAtualizarSerializer,
        responses={
            200: OpenApiResponse(description="Empresa atualizada com sucesso"),
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            404: OpenApiResponse(
                description=_EMPRESA_NAO_ENCONTRADA_DESCRIPTION
            ),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de atualização de empresa",
                request_only=True,
                value=_EMPRESA_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Empresa atualizada com sucesso",
                response_only=True,
                value=_EMPRESA_EXEMPLO_SAIDA,
            ),
        ],
    ),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(
        tags=["Empresa"],
        summary="Remove uma empresa",
        description="Remove uma empresa existente do sistema.",
        operation_id="deletarEmpresa",
        responses={
            204: OpenApiResponse(description="Empresa removida com sucesso"),
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            404: OpenApiResponse(
                description=_EMPRESA_NAO_ENCONTRADA_DESCRIPTION
            ),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
    ),
)
