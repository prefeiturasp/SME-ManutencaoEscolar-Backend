"""Schemas do app escola."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.escola.serializers.diretoria_regional_serializers import (
    DiretoriaRegionalSerializer,
)
from apps.escola.serializers.tipo_unidade_serializers import (
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
            OpenApiParameter(
                name="fields",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Lista de campos que devem ser retornados, "
                    "separados por vírgula. Exemplo: uuid,sigla"
                ),
                examples=[
                    OpenApiExample(
                        "UUID e sigla",
                        value="uuid,sigla",
                    ),
                    OpenApiExample(
                        "Somente sigla",
                        value="sigla",
                    ),
                ],
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


UNIDADE_EDUCACIONAL = extend_schema_view(
    list=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Lista unidades educacionais",
        description=(
            "Retorna as unidades educacionais cadastradas, "
            "permitindo filtrar por CODESC, tipo de escola, "
            "Diretoria Regional, unidade educacional, "
            "subprefeitura, lote e status."
        ),
        parameters=[
            OpenApiParameter(
                name="fields",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Lista de campos que devem ser retornados, "
                    "separados por vírgula. Exemplo: uuid,sigla"
                ),
                examples=[
                    OpenApiExample(
                        "UUID e nome",
                        value="uuid,nome",
                    ),
                    OpenApiExample(
                        "Somente nome",
                        value="nome",
                    ),
                ],
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Obtém uma unidade educacional",
        description="Retorna os dados de uma unidade educacional específica.",
    ),
)


SUBPREFEITURA = extend_schema_view(
    list=extend_schema(
        summary="Lista subprefeituras",
        description=(
            "Retorna a lista de subprefeituras cadastradas no sistema. "
            "Permite filtrar por código EOL e nome."
        ),
    ),
    retrieve=extend_schema(
        summary="Obtém uma subprefeitura",
        description=("Retorna os dados de uma subprefeitura específica."),
    ),
)
