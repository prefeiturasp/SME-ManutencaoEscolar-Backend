"""Schemas para a API de cargos."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.cargo.serializers import (
    CargoCriarSerializer,
    CargoSerializer,
)

_TAG_CARGO = "Cargo"

_CREDENCIAIS_INVALIDAS = "Credenciais inválidas"
_DADOS_INVALIDOS = "Dados inválidos ou cargo já cadastrado."
_ERRO_NO_SERVIDOR = "Erro no servidor"
_CARGO_NAO_ENCONTRADO = "Cargo não encontrado."
_DOCUMENTO = "Certificado NR-10"
_COMPROVANTE = "Comprovante de formação"

_ESCOLA_CONST = "ESCOLA EMEF ADMIN"

_CARGO_EXEMPLO_ENTRADA: dict[str, object] = {
    "nome": "Eletricista",
    "exige_documento": True,
    "status": True,
    "documentos": [
        {"nome": _DOCUMENTO},
        {"nome": _COMPROVANTE},
    ],
}

_CARGO_EXEMPLO_SAIDA: dict[str, object] = {
    "nome": "Eletricista",
    "exige_documento": True,
    "status": True,
    "documentos": [
        {"nome": _DOCUMENTO},
        {"nome": _COMPROVANTE},
    ],
}

_CARGO_EXEMPLO_DADOS_INVALIDOS: dict[str, object] = {
    "documentos": [
        "Informe ao menos um documento para este cargo.",
    ],
}

_CARGO_EXEMPLO_DETALHE: dict[str, object] = {
    "id": 1,
    "uuid": "77d042b4-f9d5-40fb-9c77-7aaca777a80c",
    "nome": "Engenheiro Eletricista",
    "status": True,
    "exige_documento": True,
    "documentos": [
        {"nome": "Curso Norma NR135"},
    ],
    "criado_por": 1,
    "criado_por_nome": _ESCOLA_CONST,
    "criado_em": "2026-08-21T16:47:34.072512-03:00",
    "atualizado_por": 1,
    "atualizado_por_nome": _ESCOLA_CONST,
    "username": "44331733637",
    "atualizado_em": "2026-08-21T16:47:34.072607-03:00",
}

_CARGOS_EXEMPLO_LISTAGEM: dict[str, object] = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        _CARGO_EXEMPLO_DETALHE,
    ],
}

_CARGO_EXEMPLO_ATUALIZACAO: dict[str, object] = {
    "nome": "Engenheiro Eletricista Sênior",
    "exige_documento": True,
    "status": True,
    "documentos": [
        {"nome": _DOCUMENTO},
        {"nome": _COMPROVANTE},
    ],
}

_CARGO_EXEMPLO_ATUALIZADO: dict[str, object] = {
    "nome": "Engenheiro Eletricista Sênior",
    "exige_documento": True,
    "status": True,
    "documentos": [
        {"nome": _DOCUMENTO},
        {"nome": _COMPROVANTE},
    ],
}

CARGO_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=[_TAG_CARGO],
        summary="Lista os cargos",
        description="Retorna lista paginada de cargos cadastrados no sistema.",
        operation_id="listarCargos",
        parameters=[
            OpenApiParameter(
                name="nome",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtra cargos cujo nome contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="exige_documento",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description=("Filtra cargos pela exigência de documento."),
            ),
        ],
        responses={
            200: CargoSerializer(many=True),
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
        },
        examples=[
            OpenApiExample(
                name="Lista paginada de cargos",
                response_only=True,
                status_codes=["200"],
                value=_CARGOS_EXEMPLO_LISTAGEM,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=[_TAG_CARGO],
        summary="Consulta um cargo pelo UUID",
        description="Retorna os dados de um cargo cadastrado.",
        operation_id="buscarCargoPorUuid",
        responses={
            200: CargoSerializer,
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            404: OpenApiResponse(
                description=_CARGO_NAO_ENCONTRADO,
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
        },
        examples=[
            OpenApiExample(
                name="Cargo encontrado",
                response_only=True,
                status_codes=["200"],
                value=_CARGO_EXEMPLO_DETALHE,
            ),
        ],
    ),
    create=extend_schema(
        tags=[_TAG_CARGO],
        summary="Cria um novo cargo",
        description=(
            "Cadastra um cargo e vincula os documentos informados. "
            "Quando o cargo exige documentos, ao menos um documento "
            "deve ser informado."
        ),
        operation_id="cadastrarCargo",
        request=CargoCriarSerializer,
        responses={
            201: CargoCriarSerializer,
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
                name="Exemplo de cadastro de cargo",
                request_only=True,
                value=_CARGO_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Cargo cadastrado com sucesso",
                response_only=True,
                status_codes=["201"],
                value=_CARGO_EXEMPLO_SAIDA,
            ),
            OpenApiExample(
                name="Documentos não informados",
                response_only=True,
                status_codes=["400"],
                value=_CARGO_EXEMPLO_DADOS_INVALIDOS,
            ),
        ],
    ),
    partial_update=extend_schema(
        tags=[_TAG_CARGO],
        summary="Atualiza um cargo",
        description=(
            "Atualiza os campos informados de um cargo. Quando a chave "
            "'documentos' é enviada, a lista recebida substitui os "
            "documentos anteriormente vinculados."
        ),
        operation_id="atualizarCargo",
        request=CargoCriarSerializer,
        responses={
            200: CargoCriarSerializer,
            400: OpenApiResponse(
                description=_DADOS_INVALIDOS,
            ),
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            404: OpenApiResponse(
                description=_CARGO_NAO_ENCONTRADO,
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
        },
        examples=[
            OpenApiExample(
                name="Dados para atualização",
                request_only=True,
                value=_CARGO_EXEMPLO_ATUALIZACAO,
            ),
            OpenApiExample(
                name="Cargo atualizado",
                response_only=True,
                status_codes=["200"],
                value=_CARGO_EXEMPLO_ATUALIZADO,
            ),
            OpenApiExample(
                name="Documentos não informados",
                response_only=True,
                status_codes=["400"],
                value=_CARGO_EXEMPLO_DADOS_INVALIDOS,
            ),
        ],
    ),
    destroy=extend_schema(
        tags=[_TAG_CARGO],
        summary="Exclui um cargo",
        description=(
            "Realiza a exclusão lógica de um cargo identificado pelo UUID."
        ),
        operation_id="excluirCargo",
        request=None,
        responses={
            204: OpenApiResponse(
                description="Cargo excluído com sucesso",
            ),
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            404: OpenApiResponse(
                description=_CARGO_NAO_ENCONTRADO,
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
        },
    ),
)
