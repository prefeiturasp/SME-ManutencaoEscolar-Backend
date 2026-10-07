"""Schemas para a API de equipes."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.equipe.serializers import EquipeCriarSerializer

_TAG_EQUIPE = "Equipe"

_EQUIPE_EXEMPLO_ENTRADA: dict[str, object] = {
    "nome": "Equipe Elétrica",
    "situacao": True,
    "empresa": "1d7c7c7c-8a7a-4b81-8a2a-0123456789ab",
    "lote": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    "profissionais": [
        {
            "profissional": "3f8e8e8e-0c9c-4da3-ac4c-234567890bcd",
            "funcao": "4a9f9f9f-1d0d-4eb4-bd5d-345678901cde",
        }
    ],
}

_EQUIPE_EXEMPLO_SAIDA: dict[str, object] = {
    "uuid": "5b0a0a0a-2e1e-4fc5-ce6e-456789012def",
    **_EQUIPE_EXEMPLO_ENTRADA,
    "profissionais": [
        {
            "profissional": "3f8e8e8e-0c9c-4da3-ac4c-234567890bcd",
            "cpf": "12345678901",
            "nome": "João Eletricista",
            "funcao": "4a9f9f9f-1d0d-4eb4-bd5d-345678901cde",
            "nome_funcao": "Eletricista",
        }
    ],
}

_EQUIPE_EXEMPLO_ERRO: dict[str, object] = {
    "title": "Já existe uma equipe com este nome!",
    "detail": (
        "Já existe uma equipe com o nome Equipe Elétrica cadastrada na "
        "empresa Empresa Exemplo. Para cadastrar uma nova equipe, informe "
        "um nome diferente."
    ),
}


EQUIPE_SCHEMA = extend_schema_view(
    create=extend_schema(
        tags=[_TAG_EQUIPE],
        summary="Cria uma nova equipe",
        description=(
            "Cadastra uma equipe para uma empresa e um lote, vinculando ao "
            "menos um profissional e sua respectiva função."
        ),
        operation_id="cadastrarEquipe",
        request=EquipeCriarSerializer,
        responses={
            201: EquipeCriarSerializer,
            400: OpenApiResponse(
                description=(
                    "Dados inválidos, nome de equipe já cadastrado ou "
                    "profissional indisponível para vínculo."
                )
            ),
            401: OpenApiResponse(description="Credenciais inválidas"),
            500: OpenApiResponse(description="Erro no servidor"),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de cadastro de equipe",
                request_only=True,
                value=_EQUIPE_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Equipe cadastrada com sucesso",
                response_only=True,
                status_codes=["201"],
                value=_EQUIPE_EXEMPLO_SAIDA,
            ),
            OpenApiExample(
                name="Nome de equipe já cadastrado",
                response_only=True,
                status_codes=["400"],
                value=_EQUIPE_EXEMPLO_ERRO,
            ),
        ],
    )
)
