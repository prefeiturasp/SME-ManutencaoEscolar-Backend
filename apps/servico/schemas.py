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

_TAG_SERVICO = "Serviço"
_CREDENCIAIS_INVALIDAS = "Credenciais inválidas"
_ERRO_NO_SERVIDOR = "Erro no servidor"

_SERVICO_EXEMPLO_ENTRADA = {
    "nome": "Pintura",
    "status": True,
}

_SERVICO_EXEMPLO_PATCH = {
    "nome": "Pintura externa",
    "status": True,
}

_SERVICO_EXEMPLO_SAIDA = {
    "id": 1,
    "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    **_SERVICO_EXEMPLO_ENTRADA,
}

_SERVICO_EXEMPLO_ATUALIZADO = {
    **_SERVICO_EXEMPLO_SAIDA,
    **_SERVICO_EXEMPLO_PATCH,
}

SERVICO_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=[_TAG_SERVICO],
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
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
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
        tags=[_TAG_SERVICO],
        summary="Cria um novo serviço",
        description="Adiciona um novo serviço ao sistema.",
        operation_id="cadastrarServico",
        request=ServicoCriarSerializer,
        responses={
            201: ServicoSerializer,
            400: OpenApiResponse(
                description="Dados inválidos",
            ),
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
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
    partial_update=extend_schema(
        tags=[_TAG_SERVICO],
        summary="Atualiza parcialmente um serviço",
        description=(
            "Atualiza um ou mais campos de um serviço identificado pelo UUID."
        ),
        operation_id="atualizarServico",
        request=ServicoCriarSerializer,
        responses={
            200: ServicoSerializer,
            400: OpenApiResponse(
                description="Dados inválidos ou nome já cadastrado",
            ),
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            404: OpenApiResponse(
                description="Serviço não encontrado",
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
        },
        examples=[
            OpenApiExample(
                name="Atualização parcial do nome",
                description=(
                    "No PATCH, somente os campos que serão alterados "
                    "precisam ser enviados."
                ),
                request_only=True,
                value=_SERVICO_EXEMPLO_PATCH,
            ),
            OpenApiExample(
                name="Serviço atualizado com sucesso",
                response_only=True,
                value=_SERVICO_EXEMPLO_ATUALIZADO,
            ),
        ],
    ),
)