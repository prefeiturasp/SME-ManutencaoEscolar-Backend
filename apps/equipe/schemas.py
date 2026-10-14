"""Schemas para a API de equipes."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)

from apps.equipe.serializers import (
    EquipeCriarEditarSerializer,
    EquipeListSerializer,
)

_TAG_EQUIPE = "Equipe"
_CREDENCIAIS_INVALIDAS = "Credenciais inválidas"
_ERRO_SERVIDOR = "Erro no servidor"
_EQUIPE_ATUALIZADA_SUCESSO = "Equipe atualizada com sucesso"

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

_EQUIPES_EXEMPLO_LISTAGEM: dict[str, object] = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "nome": "Equipe Elétrica",
            "nome_empresa": "Empresa Exemplo",
            "lote": {
                "nome": "Lote Centro",
                "periodo_inicial": "2026-01-01",
                "periodo_final": "2026-12-31",
            },
            "situacao": True,
        }
    ],
}


EQUIPE_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=[_TAG_EQUIPE],
        summary="Lista as equipes",
        description=(
            "Retorna a lista paginada de equipes cadastradas, com dados "
            "resumidos da empresa e do lote."
        ),
        operation_id="listarEquipes",
        parameters=[
            OpenApiParameter(
                name="nome",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtra equipes cujo nome contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="empresa",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtra equipes cujo nome da empresa contenha o valor "
                    "informado."
                ),
            ),
            OpenApiParameter(
                name="lote",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtra equipes cujo nome do lote contenha o valor "
                    "informado."
                ),
            ),
            OpenApiParameter(
                name="situacao",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filtra equipes pela situação ativa ou inativa.",
            ),
        ],
        responses={
            200: EquipeListSerializer(many=True),
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
        examples=[
            OpenApiExample(
                name="Lista paginada de equipes",
                response_only=True,
                status_codes=["200"],
                value=_EQUIPES_EXEMPLO_LISTAGEM,
            )
        ],
    ),
    create=extend_schema(
        tags=[_TAG_EQUIPE],
        summary="Cria uma nova equipe",
        description=(
            "Cadastra uma equipe para uma empresa e um lote, vinculando ao "
            "menos um profissional e sua respectiva função."
        ),
        operation_id="cadastrarEquipe",
        request=EquipeCriarEditarSerializer,
        responses={
            201: EquipeCriarEditarSerializer,
            400: OpenApiResponse(
                description=(
                    "Dados inválidos, nome de equipe já cadastrado ou "
                    "profissional indisponível para vínculo."
                )
            ),
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
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
    ),
    update=extend_schema(
        tags=[_TAG_EQUIPE],
        summary="Atualiza uma equipe",
        description=(
            "Atualiza integralmente uma equipe identificada pelo UUID e "
            "sincroniza seus profissionais. Os profissionais informados são "
            "mantidos ou vinculados, e os omitidos são removidos da equipe."
        ),
        operation_id="atualizarEquipe",
        request=EquipeCriarEditarSerializer,
        responses={
            200: OpenApiResponse(
                response=EquipeCriarEditarSerializer,
                description=_EQUIPE_ATUALIZADA_SUCESSO,
            ),
            400: OpenApiResponse(
                description=(
                    "Dados inválidos, nome de equipe já cadastrado ou "
                    "profissional indisponível para vínculo."
                )
            ),
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            404: OpenApiResponse(description="Equipe não encontrada"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de atualização de equipe",
                request_only=True,
                value={
                    **_EQUIPE_EXEMPLO_ENTRADA,
                    "nome": "Equipe Elétrica Atualizada",
                },
            ),
            OpenApiExample(
                name=_EQUIPE_ATUALIZADA_SUCESSO,
                response_only=True,
                status_codes=["200"],
                value={
                    **_EQUIPE_EXEMPLO_SAIDA,
                    "nome": "Equipe Elétrica Atualizada 2",
                },
            ),
            OpenApiExample(
                name="Nome de equipe já cadastrado",
                response_only=True,
                status_codes=["400"],
                value=_EQUIPE_EXEMPLO_ERRO,
            ),
        ],
    ),
    partial_update=extend_schema(
        tags=[_TAG_EQUIPE],
        summary="Atualiza parcialmente uma equipe",
        description=(
            "Atualiza apenas os campos informados de uma equipe identificada "
            "pelo UUID. Os profissionais são sincronizados somente quando o "
            "campo profissionais é enviado."
        ),
        operation_id="atualizarParcialmenteEquipe",
        request=EquipeCriarEditarSerializer,
        responses={
            200: OpenApiResponse(
                response=EquipeCriarEditarSerializer,
                description=_EQUIPE_ATUALIZADA_SUCESSO,
            ),
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            404: OpenApiResponse(description="Equipe não encontrada"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de atualização parcial de equipe",
                request_only=True,
                value={"nome": "Equipe Elétrica Atualizada"},
            ),
        ],
    ),
)
