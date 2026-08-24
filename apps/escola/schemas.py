"""Schemas do app escola."""

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.escola.serializers import (
    DiretoriaRegionalSerializer,
    TipoEscolaSerializer,
)

TAG_ESCOLA = "Escola"

TIPO_ESCOLA = extend_schema_view(
    list=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Lista os tipos de escola",
        description=(
            "Retorna a lista de tipos de unidade escolar cadastrados. "
            "Este endpoint permite somente a consulta dos registros."
        ),
        operation_id="listarTipoEscola",
        parameters=[
            OpenApiParameter(
                name="sigla",
                type=str,
                description=(
                    "Filtra os tipos de escola cuja a sigla contenha o valor "
                    "informado."
                ),
            ),
        ],
        responses={
            200: TipoEscolaSerializer(many=True),
        },
    ),
    retrieve=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Consulta um tipo de escola",
        description=(
            "Retorna os dados de um tipo de unidade escolar "
            "identificado pelo UUID."
        ),
        operation_id="obterTipoEscola",
        responses={
            200: TipoEscolaSerializer,
            404: OpenApiResponse(
                description="Tipo não encontrado",
            ),
        },
    ),
)

DIRETORIA_REGIONAL = extend_schema_view(
    list=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Lista as diretorias regionais",
        description=(
            "Retorna a lista paginada de Diretorias Regionais de "
            "Educação cadastradas. Este endpoint permite somente "
            "a consulta dos registros."
        ),
        operation_id="listarDiretoriasRegionais",
        responses={
            200: DiretoriaRegionalSerializer(many=True),
        },
    ),
    retrieve=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Consulta uma diretoria regional",
        description=(
            "Retorna os dados de uma Diretoria Regional de Educação "
            "identificada pelo ID."
        ),
        operation_id="obterDiretoriaRegional",
        responses={
            200: DiretoriaRegionalSerializer,
            404: OpenApiResponse(
                description="Diretoria regional não encontrada",
            ),
        },
    ),
)
