"""Schemas para a API de lotes."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.lote.serializers import (
    LoteCriarSerializer,
    LoteSerializer,
)

_TAG_LOTE = "Lote"

_CREDENCIAIS_INVALIDAS = "Credenciais inválidas"

_DADOS_INVALIDOS = "Dados inválidos, lote duplicado ou DRE já vinculada."

_ERRO_NO_SERVIDOR = "Erro no servidor"

_ESCOLA_CONST = "ESCOLA EMEF ADMIN"

_LOTE_EXEMPLO_ENTRADA: dict[str, object] = {
    "codigo_cadastro": "LOTE-00123",
    "nome": "Lote de manutenção 2026",
    "status": True,
    "empresa": "f882ef71-1705-46cb-850b-c404650d95e5",
    "periodo_inicial": "2026-08-01",
    "periodo_final": "2026-12-31",
    "diretorias_regionais": [1],
}

_LOTE_EXEMPLO_SAIDA: dict[str, object] = {
    "nome": "Lote de manutenção 2026",
    "codigo_cadastro": "LOTE-00123",
    "empresa": "eaa39861-5212-4817-9ba1-a81285985599",
    "periodo_inicial": "2026-08-01",
    "periodo_final": "2026-12-31",
    "status": True,
    "diretorias_regionais": [
        1
    ],
}

_LOTE_EXEMPLO_ATUALIZACAO: dict[str, object] = {
    "codigo_cadastro": "DRE GUAIANASES",
    "nome": "DRE GUAIANASES ATUALIZADO",
    "status": False,
    "empresa": "f882ef71-1705-46cb-850b-c404650d95e5",
    "periodo_inicial": "2026-07-27",
    "periodo_final": "2026-08-03",
    "diretorias_regionais": [13, 11],
}

_LOTE_EXEMPLO_DIRETORIA_REGIONAL_VINCULADA: dict[str, object] = {
    "title": "DIRETORIA REGIONAL já vinculada",
    "detail": (
        "Uma ou mais Diretorias Regionais já estão vinculadas a outro lote. "
        "Diretorias Regionais: 2."
    ),
}

_LOTES_EXEMPLO_LISTAGEM: dict[str, object] = {
    "count": 4,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 11,
            "uuid": "77d042b4-f9d5-40fb-9c77-7aaca777a80c",
            "codigo_cadastro": "Lote0001",
            "nome": "Lote",
            "status": True,
            "empresa": "eaa39861-5212-4817-9ba1-a81285985599",
            "periodo_inicial": "2026-07-29",
            "periodo_final": "2026-08-14",
            "diretorias_regionais": [
                {
                    "id": 1,
                    "codigo": "108700",
                    "nome": ("DIRETORIA REGIONAL DE EDUCACAO ITAQUERA"),
                    "abreviacao": "DRE - IQ",
                    "nome_curto": "DRE ITAQUERA",
                },
            ],
            "criado_por": 1,
            "criado_por_nome": _ESCOLA_CONST,
            "criado_em": "2026-08-21T16:47:34.072512-03:00",
            "atualizado_por": 1,
            "atualizado_por_nome": _ESCOLA_CONST,
            "username": "44331733637",
            "atualizado_em": "2026-08-21T16:47:34.072607-03:00",
        },
    ],
}

LOTE_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=[_TAG_LOTE],
        summary="Lista os lotes",
        description=(
            "Retorna a lista paginada de lotes cadastrados no sistema."
        ),
        operation_id="listarLotes",
        parameters=[
            OpenApiParameter(
                name="codigo_cadastro",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtra lotes cujo código de cadastro contenha "
                    "o valor informado."
                ),
            ),
            OpenApiParameter(
                name="nome",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtra lotes cujo nome contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtra lotes pelo status.",
                enum=["true", "false"],
            ),
            OpenApiParameter(
                name="empresa",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filtra pelo identificador da empresa.",
            ),
            OpenApiParameter(
                name="diretorias_regionais",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtra pelos identificadores das Diretorias Regionais, "
                    "separados por vírgula. Exemplo: 1,2,3."
                ),
            ),
            OpenApiParameter(
                name="periodo_inicial",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtra lotes com período inicial maior ou igual "
                    "à data informada."
                ),
            ),
            OpenApiParameter(
                name="periodo_final",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtra lotes com período final menor ou igual "
                    "à data informada."
                ),
            ),
        ],
        responses={
            200: LoteSerializer(many=True),
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
        },
        examples=[
            OpenApiExample(
                name="Lista paginada de lotes",
                response_only=True,
                status_codes=["200"],
                value=_LOTES_EXEMPLO_LISTAGEM,
            ),
        ],
    ),
    create=extend_schema(
        tags=[_TAG_LOTE],
        summary="Cria um novo lote",
        description=(
            "Cadastra um lote e vincula as Diretorias Regionais informadas. "
            "Cada Diretoria Regional pode estar vinculada a somente um lote."
        ),
        operation_id="cadastrarLote",
        request=LoteCriarSerializer,
        responses={
            201: LoteSerializer,
            400: OpenApiResponse(
                description=_DADOS_INVALIDOS,
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
                name="Exemplo de cadastro de lote",
                request_only=True,
                value=_LOTE_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Lote cadastrado com sucesso",
                response_only=True,
                status_codes=["201"],
                value=_LOTE_EXEMPLO_SAIDA,
            ),
            OpenApiExample(
                name="Diretoria Regional já vinculada",
                response_only=True,
                status_codes=["400"],
                value=_LOTE_EXEMPLO_DIRETORIA_REGIONAL_VINCULADA,
            ),
        ],
    ),
    partial_update=extend_schema(
        tags=[_TAG_LOTE],
        summary="Atualiza parcialmente um lote",
        description=(
            "Atualiza os campos informados de um lote identificado pelo UUID. "
            "Quando as Diretorias Regionais são informadas, seus vínculos são "
            "sincronizados. Cada Diretoria Regional pode estar vinculada a "
            "somente um lote."
        ),
        operation_id="atualizarLote",
        request=LoteCriarSerializer,
        responses={
            200: LoteSerializer,
            400: OpenApiResponse(
                description=_DADOS_INVALIDOS,
            ),
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            404: OpenApiResponse(
                description="Lote não encontrado",
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de atualização parcial do lote",
                request_only=True,
                value=_LOTE_EXEMPLO_ATUALIZACAO,
            ),
            OpenApiExample(
                name="Lote atualizado com sucesso",
                response_only=True,
                status_codes=["200"],
                value=_LOTE_EXEMPLO_SAIDA,
            ),
            OpenApiExample(
                name="Diretoria Regional já vinculada",
                response_only=True,
                status_codes=["400"],
                value=_LOTE_EXEMPLO_DIRETORIA_REGIONAL_VINCULADA,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=[_TAG_LOTE],
        summary="Busca um lote",
        description="Retorna os dados de um lote pelo UUID.",
        operation_id="buscarLote",
        responses={
            200: LoteSerializer,
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            404: OpenApiResponse(
                description="Lote não encontrado",
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
        },
        examples=[
            OpenApiExample(
                name="Detalhes do lote",
                response_only=True,
                status_codes=["200"],
                value=_LOTE_EXEMPLO_SAIDA,
            ),
        ],
    ),
)
