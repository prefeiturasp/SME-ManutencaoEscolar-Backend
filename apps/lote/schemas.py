"""Schemas para a API de lotes."""

from drf_spectacular.utils import (
    OpenApiExample,
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
_DADOS_INVALIDOS = (
    "Dados inválidos, lote duplicado ou DRE já vinculada."
)
_ERRO_NO_SERVIDOR = "Erro no servidor"

_LOTE_EXEMPLO_ENTRADA: dict[str, object] = {
    "codigo_cadastro": "LOTE-001",
    "nome": "Lote de manutenção 2026",
    "status": True,
    "empresa": 1,
    "periodo_inicial": "2026-08-01",
    "periodo_final": "2026-12-31",
    "dres": [1, 2, 3],
}

_LOTE_EXEMPLO_SAIDA: dict[str, object] = {
    "id": 1,
    "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    "codigo_cadastro": "LOTE-001",
    "nome": "Lote de manutenção 2026",
    "status": True,
    "empresa": 1,
    "periodo_inicial": "2026-08-01",
    "periodo_final": "2026-12-31",
    "dres": [1, 2, 3],
    "criado_por": 1,
    "criado_por_nome": "Matheus Bonaretti",
    "criado_em": "2026-08-19T10:00:00-03:00",
    "atualizado_por": 1,
    "atualizado_por_nome": "Matheus Bonaretti",
    "username": "matheus.simoes",
    "atualizado_em": "2026-08-19T10:00:00-03:00",
}

_LOTE_EXEMPLO_DRE_VINCULADA: dict[str, object] = {
    "title": "DRE já vinculada",
    "detail": (
        "Uma ou mais DREs já estão vinculadas a outro lote. DREs: 2."
    ),
}

LOTE_SCHEMA = extend_schema_view(
    create=extend_schema(
        tags=[_TAG_LOTE],
        summary="Cria um novo lote",
        description=(
            "Cadastra um lote e vincula as DREs informadas. "
            "Cada DRE pode estar vinculada a somente um lote."
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
                name="DRE já vinculada",
                response_only=True,
                status_codes=["400"],
                value=_LOTE_EXEMPLO_DRE_VINCULADA,
            ),
        ],
    ),
)
