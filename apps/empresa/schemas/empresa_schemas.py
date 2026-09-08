"""Schemas para a API de Empresa."""

from typing import Any

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.empresa.serializers.empresa_serializers import (
    EmpresaCriarAtualizarSerializer,
    EmpresaSerializer,
)

_USUARIO_EXEMPLO = "Usuário Exemplo"
_DATA_HORA_EXEMPLO = "2026-09-04T10:00:00-03:00"

_EMPRESA_EXEMPLO_BASE = {
    "nome": "Empresa Exemplo",
    "cnpj": "12345678000195",
    "status": True,
    "razao_social": "Empresa Exemplo LTDA",
    "link_rastreio": "https://www.exemplo.com/rastreio",
    "cep": "12345678",
    "logradouro": "Rua Exemplo",
    "numero": "123",
    "complemento": "Apto 101",
    "cidade": "Cidade Exemplo",
    "estado": "SP",
}

_RESPONSAVEIS_EXEMPLO_ENTRADA: list[dict[str, Any]] = [
    {
        "tipo": "preposto",
        "nome": "Maria da Silva",
        "email": "maria.silva@exemplo.com",
        "numero_crea": "",
        "telefone": "11987654321",
        "numero_art": "",
        "arquivos": [],
    },
    {
        "tipo": "engenheiro_civil",
        "nome": "João Souza",
        "email": "joao.souza@exemplo.com",
        "numero_crea": "1234567890",
        "telefone": "11912345678",
        "numero_art": "ART123456",
        "arquivos": [{"arquivo": "art-engenheiro.pdf"}],
    },
]

_EMPRESA_EXEMPLO_ENTRADA = {
    **_EMPRESA_EXEMPLO_BASE,
    "responsaveis_tecnicos": _RESPONSAVEIS_EXEMPLO_ENTRADA,
}

_EMPRESA_EXEMPLO_SAIDA = {
    "id": 1,
    "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
    **_EMPRESA_EXEMPLO_BASE,
    "criado_por": _USUARIO_EXEMPLO,
    "criado_em": _DATA_HORA_EXEMPLO,
    "atualizado_por": _USUARIO_EXEMPLO,
    "atualizado_em": _DATA_HORA_EXEMPLO,
    "responsaveis_tecnicos": [
        {
            **responsavel,
            "uuid": uuid,
            "arquivos": arquivos,
            "criado_por": _USUARIO_EXEMPLO,
            "criado_em": _DATA_HORA_EXEMPLO,
            "atualizado_por": _USUARIO_EXEMPLO,
            "atualizado_em": _DATA_HORA_EXEMPLO,
        }
        for responsavel, uuid, arquivos in (
            (
                _RESPONSAVEIS_EXEMPLO_ENTRADA[0],
                "5c48fbbc-b488-423c-9bd8-81d46fba45b1",
                [],
            ),
            (
                _RESPONSAVEIS_EXEMPLO_ENTRADA[1],
                "221fbbdd-c1e0-4144-a852-620c466de8f7",
                [
                    {
                        "uuid": "504b59f5-01a4-48f8-8118-ae158f31c312",
                        "nome": "art-engenheiro.pdf",
                        "arquivo_url": (
                            "https://arquivos.exemplo.com/art-engenheiro.pdf"
                        ),
                        "anexado_por": _USUARIO_EXEMPLO,
                        "anexado_em": _DATA_HORA_EXEMPLO,
                    }
                ],
            ),
        )
    ],
}

_EMPRESA_EXEMPLO_ATUALIZACAO = {
    **_EMPRESA_EXEMPLO_ENTRADA,
    "responsaveis_tecnicos": [
        {
            **_RESPONSAVEIS_EXEMPLO_ENTRADA[0],
            "uuid": "5c48fbbc-b488-423c-9bd8-81d46fba45b1",
        },
        {
            **_RESPONSAVEIS_EXEMPLO_ENTRADA[1],
            "uuid": "221fbbdd-c1e0-4144-a852-620c466de8f7",
            "arquivos": [
                {"uuid": "504b59f5-01a4-48f8-8118-ae158f31c312"},
                {"arquivo": "novo-laudo.pdf"},
            ],
        },
    ],
}

_REGRAS_RESPONSAVEIS_DESCRIPTION = (
    " Deve ser informado ao menos um responsável técnico, sem repetir o "
    "tipo (`preposto`, `engenheiro_civil` ou `engenheiro_eletricista`). "
    "Engenheiros devem possuir ao menos um item em `arquivos`. Cada item "
    "pode enviar um novo arquivo em `arquivo` ou informar o `uuid` de um "
    "anexo existente para preservá-lo durante a atualização."
)

_CREDENCIAL_INVALID_DESCRIPTION = "Credenciais inválidas"
_ERRO_SERVIDOR_DESCRIPTION = "Erro no servidor"
_EMPRESA_NAO_ENCONTRADA_DESCRIPTION = "Empresa não encontrada"

EMPRESA_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=["Empresa"],
        summary="Lista as empresas",
        description="Retorna a lista de empresas cadastradas no sistema.",
        operation_id="listarEmpresas",
        parameters=[
            OpenApiParameter(
                name="nome",
                type=str,
                description=(
                    "Filtra empresas cujo nome contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="razao_social",
                type=str,
                description=(
                    "Filtra empresas cuja razão social contenha o "
                    "valor informado."
                ),
            ),
            OpenApiParameter(
                name="cnpj",
                type=str,
                description=(
                    "Filtra empresas cujo CNPJ contenha o valor informado."
                ),
            ),
            OpenApiParameter(
                name="status",
                type=bool,
                description="Filtra empresas pelo status (ativo/inativo).",
            ),
        ],
        responses={
            200: EmpresaSerializer(many=True),
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
        examples=[
            OpenApiExample(
                name="Lista de empresas",
                response_only=True,
                value=_EMPRESA_EXEMPLO_SAIDA,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Empresa"],
        summary="Detalhes de uma empresa",
        description="Retorna os detalhes de uma empresa específica.",
        operation_id="detalharEmpresa",
        responses={
            200: EmpresaSerializer,
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            404: OpenApiResponse(
                description=_EMPRESA_NAO_ENCONTRADA_DESCRIPTION
            ),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
        examples=[
            OpenApiExample(
                name="Detalhes da empresa",
                response_only=True,
                value=_EMPRESA_EXEMPLO_SAIDA,
            ),
        ],
    ),
    create=extend_schema(
        tags=["Empresa"],
        summary="Cria uma nova empresa",
        description=(
            "Adiciona uma nova empresa ao sistema."
            + _REGRAS_RESPONSAVEIS_DESCRIPTION
        ),
        operation_id="cadastrarEmpresa",
        request=EmpresaCriarAtualizarSerializer,
        responses={
            201: OpenApiResponse(
                response=EmpresaSerializer,
                description="Empresa criada com sucesso",
            ),
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de cadastro de empresa",
                request_only=True,
                value=_EMPRESA_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Empresa criada com sucesso",
                response_only=True,
                value=_EMPRESA_EXEMPLO_SAIDA,
            ),
        ],
    ),
    update=extend_schema(
        tags=["Empresa"],
        summary="Atualiza uma empresa",
        description=(
            "Atualiza integralmente os dados de uma empresa existente."
            + _REGRAS_RESPONSAVEIS_DESCRIPTION
        ),
        operation_id="atualizarEmpresa",
        request=EmpresaCriarAtualizarSerializer,
        responses={
            200: OpenApiResponse(
                response=EmpresaSerializer,
                description="Empresa atualizada com sucesso",
            ),
            400: OpenApiResponse(description="Dados inválidos"),
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            404: OpenApiResponse(
                description=_EMPRESA_NAO_ENCONTRADA_DESCRIPTION
            ),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de atualização de empresa",
                request_only=True,
                value=_EMPRESA_EXEMPLO_ATUALIZACAO,
            ),
            OpenApiExample(
                name="Empresa atualizada com sucesso",
                response_only=True,
                value=_EMPRESA_EXEMPLO_SAIDA,
            ),
        ],
    ),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(
        tags=["Empresa"],
        summary="Remove uma empresa",
        description="Remove uma empresa existente do sistema.",
        operation_id="deletarEmpresa",
        responses={
            204: OpenApiResponse(description="Empresa removida com sucesso"),
            401: OpenApiResponse(description=_CREDENCIAL_INVALID_DESCRIPTION),
            404: OpenApiResponse(
                description=_EMPRESA_NAO_ENCONTRADA_DESCRIPTION
            ),
            503: OpenApiResponse(description="Instabilidade"),
            500: OpenApiResponse(description=_ERRO_SERVIDOR_DESCRIPTION),
        },
    ),
)
