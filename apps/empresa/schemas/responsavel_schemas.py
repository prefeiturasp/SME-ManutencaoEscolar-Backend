"""Schemas para a API de Responsável Técnico."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.empresa.serializers.responsavel_serializers import (
    ResponsavelTecnicoSerializer,
)

_RESPONSAVEL_EXEMPLO_ENTRADA = {
    "empresa": "345gty-4567-8901-2345-67890abcdef",
    "nome": "Responsavel Exemplo",
    "tipo": "preposto",
    "numero_crea": "123456789",
    "numero_art": "123456789",
    "email": "responsavel.exemplo@exemplo.com",
    "telefone": "11987654321",
}

_RESPONSAVEL_EXEMPLO_SAIDA = {
    "id": 1,
    "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    **_RESPONSAVEL_EXEMPLO_ENTRADA,
}

_CREDENCIAL_INVALID_DESCRIPTION = "Credenciais inválidas"
_ERRO_SERVIDOR_DESCRIPTION = "Erro no servidor"

RESPONSAVEL_SCHEMA = extend_schema_view(
    create=extend_schema(
        tags=["Responsável Técnico"],
        summary="Cria um novo Responsável Técnico",
        description="Adiciona um novo Responsável Técnico ao sistema.",
        operation_id="cadastrarResponsavelTecnico",
        request=ResponsavelTecnicoSerializer,
        responses={
            201: OpenApiResponse(
                description="Responsável Técnico criado com sucesso"
            ),
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de cadastro de Responsável Técnico",
                request_only=True,
                value=_RESPONSAVEL_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Responsável Técnico criado com sucesso",
                response_only=True,
                value=_RESPONSAVEL_EXEMPLO_SAIDA,
            ),
        ],
    ),
)
