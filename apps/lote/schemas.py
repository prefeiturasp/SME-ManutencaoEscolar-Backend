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

_DADOS_INVALIDOS = "Dados inválidos, lote duplicado ou DRE já vinculada."

_ERRO_NO_SERVIDOR = "Erro no servidor"

_LOTE_EXEMPLO_ENTRADA: dict[str, object] = {
    "codigo_cadastro": "LOTE-00123",
    "nome": "Lote de manutenção 2026",
    "status": True,
    "empresa": 1,
    "periodo_inicial": "2026-08-01",
    "periodo_final": "2026-12-31",
    "diretorias_regionais": [1],
}

_LOTE_EXEMPLO_SAIDA: dict[str, object] = {
    "nome": "Lote de manutenção 2026",
    "codigo_cadastro": "LOTE-00123",
    "empresa": {
        "id": 1,
        "uuid": "eaa39861-5212-4817-9ba1-a81285985599",
        "nome": "Empresa teste Vinculo",
        "cnpj": "99889215000172",
        "status": True,
        "razao_social": "Empresa teste Vinculo",
        "link_rastreio": "",
        "cep": "13060770",
        "logradouro": "XPTO",
        "numero": "120",
        "complemento": "",
        "cidade": "Campinas",
        "estado": "PI",
        "criado_por": "ESCOLA EMEF ADMIN",
        "criado_em": "2026-08-19T12:04:00.313114-03:00",
        "atualizado_por": None,
        "atualizado_em": "2026-08-19T12:04:00.313142-03:00",
    },
    "periodo_inicial": "2026-08-01",
    "periodo_final": "2026-12-31",
    "status": True,
    "diretorias_regionais": [
        {
            "id": 1,
            "codigo": "108700",
            "nome": "DIRETORIA REGIONAL DE EDUCACAO ITAQUERA",
            "abreviacao": "DRE - IQ",
        },
    ],
}

_LOTE_EXEMPLO_DIRETORIA_REGIONAL_VINCULADA: dict[str, object] = {
    "title": "DIRETORIA REGIONAL já vinculada",
    "detail": (
        "Uma ou mais Diretorias Regionais já estão vinculadas a outro lote."
        "Diretorias Regionais: 2."
    ),
}

LOTE_SCHEMA = extend_schema_view(
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
)
