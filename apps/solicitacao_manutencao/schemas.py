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
    SolicitacaoManutencaoCriarEditarSerializer,
    SolicitacaoManutencaoDetalheSerializer,
    SolicitacaoManutencaoListSerializer,
)

_TAG_SOLICITACAO = "Solicitação de manutenção"
_CREDENCIAIS_INVALIDAS = "Credenciais inválidas."
_ERRO_SERVIDOR = "Erro no servidor."
_REPARO_PRIORITARIO = "Reparo prioritário."
_DISJUNTOR_DESARMADO = "Disjuntor desarmando constantemente."

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

_SOLICITACAO_EDICAO_RESPOSTA_SERIALIZER = inline_serializer(
    name="SolicitacaoManutencaoEdicaoResposta",
    fields={
        "uuid": serializers.UUIDField(),
        "codigo": serializers.CharField(),
        "tipo_atendimento": serializers.CharField(),
        "informacoes_adicionais": serializers.CharField(),
        "unidade_educacional": serializers.UUIDField(),
        "situacao": serializers.CharField(),
        "data_envio": serializers.DateTimeField(allow_null=True),
        "fase": serializers.CharField(),
        "servicos": inline_serializer(
            name="ServicoManutencaoEdicaoResposta",
            many=True,
            fields={
                "uuid": serializers.UUIDField(),
                "servico": serializers.UUIDField(allow_null=True),
                "servico_especifico": serializers.CharField(),
                "local_reparo": serializers.CharField(),
                "descricao": serializers.CharField(),
                "arquivos": inline_serializer(
                    name="FotoLocalReparoEdicaoResposta",
                    many=True,
                    fields={
                        "uuid": serializers.UUIDField(),
                        "arquivo": serializers.URLField(),
                        "nome_original": serializers.CharField(),
                    },
                ),
            },
        ),
    },
)

_SOLICITACAO_EXEMPLO_ENTRADA: dict[str, Any] = {
    "tipo_atendimento": "urgente",
    "informacoes_adicionais": _REPARO_PRIORITARIO,
    "unidade_educacional": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    "servicos": [
        {
            "servico": "3f8e8e8e-0c9c-4da3-ac4c-23456789abcd",
            "servico_especifico": "Troca de disjuntor",
            "local_reparo": "Cozinha",
            "descricao": _DISJUNTOR_DESARMADO,
            "arquivos": [
                {"arquivo": "<arquivo enviado como multipart/form-data>"}
            ],
        }
    ],
}

_SOLICITACAO_EXEMPLO_SAIDA: dict[str, Any] = {
    "uuid": "4a9f9f9f-1d0d-4eb4-bd5d-3456789abcde",
    "codigo": "0000001",
    **_SOLICITACAO_EXEMPLO_ENTRADA,
    "situacao": "aguardando_analise_dre",
    "data_envio": "2026-10-20T14:32:00-03:00",
    "fase": "solicitacao",
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

_SOLICITACAO_EDICAO_EXEMPLO_SAIDA: dict[str, Any] = {
    "uuid": "4a9f9f9f-1d0d-4eb4-bd5d-3456789abcde",
    "codigo": "0000001",
    "tipo_atendimento": "urgente",
    "informacoes_adicionais": _REPARO_PRIORITARIO,
    "unidade_educacional": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    "situacao": "aguardando_analise_dre",
    "data_envio": "2026-10-20T14:30:00-03:00",
    "fase": "solicitacao",
    "servicos": [
        {
            "uuid": "3f8e8e8e-0c9c-4da3-ac4c-23456789abcd",
            "servico": "3f8e8e8e-0c9c-4da3-ac4c-23456789abcd",
            "servico_especifico": "",
            "local_reparo": "Cozinha",
            "descricao": _DISJUNTOR_DESARMADO,
            "arquivos": [
                {
                    "uuid": "5b0a0a0a-2e1e-4fc5-ae6e-456789abcdef",
                    "arquivo": (
                        "http://localhost:9000/arquivos/2026/10/20/reparo.jpg"
                    ),
                    "nome_original": "reparo.jpg",
                }
            ],
        }
    ],
}

_SOLICITACAO_DETALHE_EXEMPLO: dict[str, Any] = {
    "uuid": "4a9f9f9f-1d0d-4eb4-bd5d-3456789abcde",
    "codigo": "0000001",
    "tipo_atendimento": "urgente",
    "informacoes_adicionais": _REPARO_PRIORITARIO,
    "unidade_educacional": {
        "id": 1,
        "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
        "codigo_eol": "1234567",
        "nome": "Antônia Barros Figueiroa",
        "diretoria_regional": {"id": 1, "nome_curto": "Freguesia/Brasilândia"},
        "tipo_escola": {
            "uuid": "6c1b1b1b-4f4f-4a1a-8c8c-567890abcdef",
            "sigla": "EMEF",
        },
        "subprefeitura": {
            "uuid": "7d2c2c2c-5a5a-4b2b-9d9d-67890abcdef1",
            "nome": "Freguesia/Brasilândia",
        },
        "lote": {
            "uuid": "8e3d3d3d-6b6b-4c3c-aeae-7890abcdef12",
            "nome": "002",
        },
        "status": True,
        "dados": {
            "email": "escola@educacao.sp.gov.br",
            "telefone": "",
            "logradouro": "Avenida João Pedroso Guimarães",
            "numero": "5214",
            "bairro": "Bela Vista",
            "cep": "09652320",
            "municipio": "São Paulo",
            "uf": "SP",
        },
        "responsaveis": [],
    },
    "situacao": "aguardando_analise_dre",
    "solicitante": "UE",
    "data_envio": "2026-10-20T14:31:00-03:00",
    "fase": "solicitacao",
    "servicos": [
        {
            "servico_uuid": "3f8e8e8e-0c9c-4da3-ac4c-23456789abcd",
            "nome_servico": "Elétrica",
            "servico_especifico": "",
            "local_reparo": "Cozinha",
            "descricao": _DISJUNTOR_DESARMADO,
            "arquivos": [
                {
                    "uuid": "5b0a0a0a-2e1e-4fc5-ae6e-456789abcdef",
                    "arquivo": "http://localhost:9000/arquivos/reparo.jpg",
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
            OpenApiParameter(
                name="data_envio_after",
                type=str,
                description="Data inicial do intervalo de envio (YYYY-MM-DD).",
            ),
            OpenApiParameter(
                name="data_envio_before",
                type=str,
                description="Data final do intervalo de envio (YYYY-MM-DD).",
            ),
            OpenApiParameter(name="fase", type=str),
            OpenApiParameter(name="situacao", type=str),
        ],
        responses={
            200: _SOLICITACOES_LISTAGEM_RESPONSE,
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
    ),
    retrieve=extend_schema(
        tags=[_TAG_SOLICITACAO],
        summary="Busca uma solicitação de manutenção",
        description="Retorna os dados de uma solicitação pelo UUID.",
        operation_id="buscarSolicitacaoManutencao",
        responses={
            200: SolicitacaoManutencaoDetalheSerializer,
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            404: OpenApiResponse(description="Solicitação não encontrada."),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
        examples=[
            OpenApiExample(
                name="Detalhes da solicitação",
                response_only=True,
                status_codes=["200"],
                value=_SOLICITACAO_DETALHE_EXEMPLO,
            )
        ],
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
        request=SolicitacaoManutencaoCriarEditarSerializer,
        responses={
            201: SolicitacaoManutencaoCriarEditarSerializer,
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
    editar_solicitacao_ue=extend_schema(
        tags=[_TAG_SOLICITACAO],
        summary="Edita uma solicitação de manutenção",
        description=(
            "Atualiza integralmente uma solicitação e sincroniza seus "
            "serviços e anexos. Informe o UUID de cada serviço e anexo "
            "existente que deve ser mantido ou atualizado; itens sem UUID "
            "serão criados e itens omitidos serão removidos."
        ),
        operation_id="editarSolicitacaoManutencao",
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
        request=SolicitacaoManutencaoCriarEditarSerializer,
        responses={
            200: _SOLICITACAO_EDICAO_RESPOSTA_SERIALIZER,
            400: OpenApiResponse(description="Dados inválidos."),
            401: OpenApiResponse(description=_CREDENCIAIS_INVALIDAS),
            404: OpenApiResponse(description="Solicitação não encontrada."),
            500: OpenApiResponse(description=_ERRO_SERVIDOR),
        },
        examples=[
            OpenApiExample(
                name="Solicitação editada",
                response_only=True,
                status_codes=["200"],
                value=_SOLICITACAO_EDICAO_EXEMPLO_SAIDA,
            ),
        ],
    ),
)
