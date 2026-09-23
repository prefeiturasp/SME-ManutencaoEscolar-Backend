"""Schemas para a API de profissionais."""

from drf_spectacular.helpers import forced_singular_serializer
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers

from apps.profissional.serializers.profissional_serializers import (
    ProfissionalCriarAtualizarSerializer,
    ProfissionalListSerializer,
)

_TAG_PROFISSIONAL = "Profissional"

_PROFISSIONAL_EXEMPLO_ENTRADA: dict[str, object] = {
    "nome": "José da Silva",
    "cpf": "12345678901",
    "rg": "123456789",
    "status": True,
    "funcoes": [
        {
            "uuid_cargo": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
            "documentos": [{"nome": "Certificado NR-10"}],
        }
    ],
}

_PROFISSIONAL_EXEMPLO_SAIDA: dict[str, object] = {
    **_PROFISSIONAL_EXEMPLO_ENTRADA,
    "funcoes": [
        {
            "uuid": "3f8e8e8e-0c9c-4da3-ac4c-234567890bcd",
            "nome_cargo": "Eletricista",
            "uuid_cargo": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
            "criado_por": "Maria Souza",
            "criado_em": "2026-09-17T10:00:00-03:00",
            "atualizado_por": None,
            "atualizado_em": "2026-09-17T10:00:00-03:00",
            "documentos": [{"nome": "Certificado NR-10"}],
        }
    ],
}

_PROFISSIONAL_EXEMPLO_DADOS_INVALIDOS: dict[str, object] = {
    "cpf": ["Já existe um profissional cadastrado com este CPF."],
}

_PROFISSIONAIS_EXEMPLO_LISTAGEM: dict[str, object] = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "uuid": "1d7c7c7c-8a7a-4b81-8a2a-0123456789ab",
            "nome": "José da Silva",
            "cpf": "12345678901",
            "rg": "123456789",
            "status": True,
            "funcoes": ["Eletricista"],
        }
    ],
}

_PROFISSIONAIS_LISTAGEM_SERIALIZER = inline_serializer(
    name="ProfissionaisListagemPaginada",
    fields={
        "count": serializers.IntegerField(),
        "next": serializers.URLField(allow_null=True),
        "previous": serializers.URLField(allow_null=True),
        "results": ProfissionalListSerializer(many=True),
    },
)
_PROFISSIONAIS_LISTAGEM_RESPONSE = forced_singular_serializer(
    _PROFISSIONAIS_LISTAGEM_SERIALIZER.__class__
)


PROFISSIONAL_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=[_TAG_PROFISSIONAL],
        summary="Lista os profissionais",
        description=(
            "Retorna a lista paginada de profissionais cadastrados, "
            "incluindo os nomes dos cargos exercidos."
        ),
        operation_id="listarProfissionais",
        parameters=[
            OpenApiParameter(
                name="nome",
                type=str,
                description=(
                    "Filtra profissionais cujo nome contenha o valor "
                    "informado."
                ),
            ),
            OpenApiParameter(
                name="cpf",
                type=str,
                description=(
                    "Filtra profissionais cujo CPF contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="rg",
                type=str,
                description=(
                    "Filtra profissionais cujo RG contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="funcao",
                type=str,
                description=(
                    "Filtra profissionais cujo nome do cargo contenha o "
                    "valor informado."
                ),
            ),
            OpenApiParameter(
                name="status",
                type=bool,
                description=(
                    "Filtra profissionais pelo status (ativo/inativo)."
                ),
            ),
        ],
        responses={
            200: _PROFISSIONAIS_LISTAGEM_RESPONSE,
            401: OpenApiResponse(description="Credenciais inválidas"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Lista de profissionais",
                response_only=True,
                status_codes=["200"],
                value=_PROFISSIONAIS_EXEMPLO_LISTAGEM,
            ),
        ],
    ),
    retrieve=extend_schema(exclude=True),
    create=extend_schema(
        tags=[_TAG_PROFISSIONAL],
        summary="Cria um novo profissional",
        description=(
            "Cadastra um profissional com ao menos uma função e vincula os "
            "documentos informados para cada cargo."
        ),
        operation_id="cadastrarProfissional",
        request=ProfissionalCriarAtualizarSerializer,
        responses={
            201: ProfissionalCriarAtualizarSerializer,
            400: OpenApiResponse(
                description=(
                    "Dados inválidos, CPF ou RG já cadastrado, função "
                    "duplicada ou documentos obrigatórios não informados."
                ),
            ),
            401: OpenApiResponse(description="Credenciais inválidas"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de cadastro de profissional",
                request_only=True,
                value=_PROFISSIONAL_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Profissional cadastrado com sucesso",
                response_only=True,
                status_codes=["201"],
                value=_PROFISSIONAL_EXEMPLO_SAIDA,
            ),
            OpenApiExample(
                name="CPF já cadastrado",
                response_only=True,
                status_codes=["400"],
                value=_PROFISSIONAL_EXEMPLO_DADOS_INVALIDOS,
            ),
        ],
    ),
)
