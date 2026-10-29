"""Schemas para a API de solicitações de manutenção."""

from typing import Any

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

from apps.solicitacao_manutencao.serializers import (
    SolicitacaoManutencaoCriarSerializer,
    SolicitacaoManutencaoListSerializer,
)

_TAG_SOLICITACAO = "Solicitação de manutenção"
_CREDENCIAIS_INVALIDAS = "Credenciais inválidas."
_ERRO_SERVIDOR = "Erro no servidor."

_SOLICITACOES_LISTAGEM_SERIALIZER = inline_serializer(
    name="SolicitacoesManutencaoListagemPaginada",
    fields={
        "count": serializers.IntegerField(),
        "next": serializers.URLField(allow_null=True),
        "previous": serializers.URLField(allow_null=True),
        "results": SolicitacaoManutencaoListSerializer(many=True),
    },
)
_SOLICITACOES_LISTAGEM_RESPONSE = forced_singular_serializer(
    _SOLICITACOES_LISTAGEM_SERIALIZER.__class__
)

_CHOICE_SERIALIZER = inline_serializer(
    name="SolicitacaoManutencaoChoice",
    fields={
        "value": serializers.CharField(),
        "label": serializers.CharField(),
    },
)

_SOLICITACAO_EXEMPLO_ENTRADA: dict[str, Any] = {
    "tipo_atendimento": "urgente",
    "informacoes_adicionais": "Reparo prioritário.",
    "unidade_educacional": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    "servicos": [
        {
            "servico": "3f8e8e8e-0c9c-4da3-ac4c-23456789abcd",
            "servico_especifico": "Troca de disjuntor",
            "local_reparo": "Cozinha",
            "descricao": "Disjuntor desarmando constantemente.",
            "arquivos": [{"arquivo": "reparo.jpg"}],
        }
    ],
}

_SOLICITACAO_EXEMPLO_SAIDA: dict[str, Any] = {
    "uuid": "4a9f9f9f-1d0d-4eb4-bd5d-3456789abcde",
    "codigo": "0000001",
    **_SOLICITACAO_EXEMPLO_ENTRADA,
    "situacao": "aguardando_analise_dre",
    "data_envio": "2026-10-20T14:30:00-03:00",
    "fase": "solicitacao",
    "solicitante": "ue",
    "servicos": [
        {
            **_SOLICITACAO_EXEMPLO_ENTRADA["servicos"][0],
            "arquivos": [
                {
                    "uuid": "5b0a0a0a-2e1e-4fc5-ae6e-456789abcdef",
                    "arquivo": (
                        "http://localhost:9000/arquivos/2026/10/20/reparo.jpg"
                    ),
                }
            ],
        }
    ],
}

SOLICITACAO_MANUTENCAO_SCHEMA = extend_schema_view(
    situacoes=extend_schema(
        tags=[_TAG_SOLICITACAO],
        summary="Lista as situações das solicitações de manutenção",
        operation_id="listarSituacoesSolicitacaoManutencao",
        responses={
            200: _CHOICE_SERIALIZER.__class__(many=True),
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
    ),
    fases=extend_schema(
        tags=[_TAG_SOLICITACAO],
        summary="Lista as fases das solicitações de manutenção",
        operation_id="listarFasesSolicitacaoManutencao",
        responses={
            200: _CHOICE_SERIALIZER.__class__(many=True),
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
    ),
    tipos_atendimento=extend_schema(
        tags=[_TAG_SOLICITACAO],
        summary="Lista os tipos de atendimento",
        operation_id="listarTiposAtendimentoSolicitacaoManutencao",
        responses={
            200: _CHOICE_SERIALIZER.__class__(many=True),
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
    ),
    list=extend_schema(
        tags=[_TAG_SOLICITACAO],
        summary="Lista as solicitações de manutenção",
        description=(
            "Retorna a lista paginada de solicitações de manutenção "
            "cadastradas."
        ),
        operation_id="listarSolicitacoesManutencao",
        parameters=[
            OpenApiParameter(name="codigo", type=str),
            OpenApiParameter(name="tipo_atendimento", type=str),
            OpenApiParameter(name="data_envio", type=str),
            OpenApiParameter(name="fase", type=str),
            OpenApiParameter(name="situacao", type=str),
        ],
        responses={
            200: _SOLICITACOES_LISTAGEM_RESPONSE,
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
    ),
    solicitacao_ue=extend_schema(
        tags=[_TAG_SOLICITACAO],
        summary="Cria uma solicitação de manutenção",
        description=(
            "Cadastra uma solicitação com ao menos um serviço de "
            "manutenção. Quando `enviar=true`, a solicitação é enviada "
            "para análise da DRE; caso contrário, permanece como não enviada."
        ),
        operation_id="criarSolicitacaoManutencao",
        parameters=[
            OpenApiParameter(
                name="enviar",
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Indica se a solicitação deve ser enviada para análise "
                    "da DRE. O valor padrão é `false`."
                ),
            )
        ],
        request=SolicitacaoManutencaoCriarSerializer,
        responses={
            201: SolicitacaoManutencaoCriarSerializer,
            400: OpenApiResponse(description="Dados inválidos."),
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de criação de solicitação",
                request_only=True,
                value=_SOLICITACAO_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Solicitação criada e enviada para a DRE",
                response_only=True,
                status_codes=["201"],
                value=_SOLICITACAO_EXEMPLO_SAIDA,
            ),
        ],
    ),
)
