"""Schemas para a API de solicitações de manutenção."""

from typing import Any

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.solicitacao_manutencao.serializers import (
    SolicitacaoManutencaoCriarSerializer,
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
    "servicos": [
        {
            **_SOLICITACAO_EXEMPLO_ENTRADA["servicos"][0],
            "arquivos": [
                {
                    "uuid": "5b0a0a0a-2e1e-4fc5-ae6e-456789abcdef",
                    "arquivo": (
                        "http://localhost:9000/arquivos/2026/10/20/"
                        "reparo.jpg"
                    ),
                }
            ],
        }
    ],
}

SOLICITACAO_MANUTENCAO_SCHEMA = extend_schema_view(
    create=extend_schema(
        tags=["Solicitação de manutenção"],
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
            401: OpenApiResponse(description="Credenciais inválidas."),
            500: OpenApiResponse(description="Erro no servidor."),
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
    )
)
