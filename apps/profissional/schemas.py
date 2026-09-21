"""Schemas para a API de profissionais."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.profissional.serializers.profissional_serializers import (
    ProfissionalCriarAtualizarSerializer,
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


PROFISSIONAL_SCHEMA = extend_schema_view(
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
