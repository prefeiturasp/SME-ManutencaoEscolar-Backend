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
from apps.escola.serializers.unidade_educacional_serializers import (
    UnidadeEducacionalAtualizarSerializer,
    UnidadeEducacionalListSerializer,
    UnidadeEducacionalSerializer,
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
            "permitindo filtrar por código eol, tipo de escola, "
            "Diretoria Regional, unidade educacional, "
            "subprefeitura, lote e status."
        ),
        parameters=[
            OpenApiParameter(
                name="codigo_eol",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Filtra pelo código EOL exato da unidade educacional."
                ),
                examples=[
                    OpenApiExample(
                        "Código EOL",
                        value="100001",
                    ),
                ],
            ),
            OpenApiParameter(
                name="tipo_escola",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtra pelo UUID do tipo de escola.",
                examples=[
                    OpenApiExample(
                        "Tipo de escola",
                        value="123e4567-e89b-12d3-a456-426614174000",
                    ),
                ],
            ),
            OpenApiParameter(
                name="diretoria_regional",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtra pelo ID da Diretoria Regional.",
                examples=[
                    OpenApiExample(
                        "Diretoria Regional",
                        value=1,
                    ),
                ],
            ),
            OpenApiParameter(
                name="unidade_educacional",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtra pelo UUID da unidade educacional.",
                examples=[
                    OpenApiExample(
                        "Unidade educacional",
                        value="123e4567-e89b-12d3-a456-426614174000",
                    ),
                ],
            ),
            OpenApiParameter(
                name="subprefeitura",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Filtra pelo UUID da subprefeitura. Utilize "
                    "`sem-subprefeitura` para retornar unidades que não "
                    "possuem subprefeitura vinculada."
                ),
                examples=[
                    OpenApiExample(
                        "Subprefeitura",
                        value="123e4567-e89b-12d3-a456-426614174000",
                    ),
                    OpenApiExample(
                        "Sem subprefeitura",
                        value="sem-subprefeitura",
                    ),
                ],
            ),
            OpenApiParameter(
                name="lote",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Filtra unidades pelo nome do lote associado à "
                    "Diretoria Regional."
                ),
                examples=[
                    OpenApiExample(
                        "Nome do lote",
                        value="Lote Centro",
                    ),
                ],
            ),
            OpenApiParameter(
                name="status",
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtra pelo status da unidade educacional.",
                examples=[
                    OpenApiExample(
                        "Unidades ativas",
                        value=True,
                    ),
                    OpenApiExample(
                        "Unidades inativas",
                        value=False,
                    ),
                ],
            ),
        ],
        responses={
            200: UnidadeEducacionalListSerializer(many=True),
        },
    ),
    retrieve=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Obtém uma unidade educacional",
        description=(
            "Retorna os dados detalhados de uma unidade educacional "
            "identificada pelo UUID, incluindo seus dados complementares, "
            "tipo de escola, Diretoria Regional, subprefeitura, lote e "
            "status."
        ),
        operation_id="obterUnidadeEducacional",
        responses={
            200: UnidadeEducacionalSerializer,
            404: OpenApiResponse(
                description="Unidade educacional não encontrada",
            ),
        },
    ),
    update=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Atualiza uma unidade educacional",
        description=(
            "Atualiza integralmente os dados de uma unidade educacional "
            "identificada pelo UUID. Os responsáveis informados com UUID "
            "existente são atualizados. Responsáveis sem UUID são criados "
            "e vinculados à unidade. Os responsáveis que possuíam vínculo "
            "ativo com a unidade, mas não forem enviados na requisição, "
            "terão o vínculo inativado e sofrerão soft-delete."
        ),
        operation_id="atualizarUnidadeEducacional",
        request=UnidadeEducacionalAtualizarSerializer,
        responses={
            200: OpenApiResponse(
                response=UnidadeEducacionalSerializer,
                description="Unidade educacional atualizada com sucesso",
            ),
            400: OpenApiResponse(
                description="Dados inválidos",
            ),
            401: OpenApiResponse(
                description="Credenciais inválidas",
            ),
            404: OpenApiResponse(
                description="Unidade educacional não encontrada",
            ),
            500: OpenApiResponse(
                description="Erro no servidor",
            ),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de atualização de unidade educacional",
                request_only=True,
                value={
                    "email": "escola@educacao.sp.gov.br",
                    "telefone": "1133334444",
                    "ativo": True,
                    "responsaveis": [
                        {
                            "uuid": ("123e4567-e89b-12d3-a456-426614174000"),
                            "registro_funcional": "1234567",
                            "nome": "JOÃO DA SILVA",
                            "cargo": "1",
                            "email": "joao.silva@email.com",
                            "telefone": "",
                            "celular": "11999999999",
                        },
                        {
                            "registro_funcional": "7654321",
                            "nome": "MARIA DA SILVA",
                            "cargo": "1",
                            "email": "maria.silva@email.com",
                            "telefone": "",
                            "celular": "11988888888",
                        },
                    ],
                },
            ),
            OpenApiExample(
                name="Unidade educacional atualizada com sucesso",
                response_only=True,
                value={
                    "id": 1,
                    "uuid": ("987e6543-e21b-45d3-a456-426614174000"),
                    "codigo_eol": "123456",
                    "nome": "EMEF EXEMPLO",
                    "status": True,
                    "responsaveis": [
                        {
                            "uuid": ("123e4567-e89b-12d3-a456-426614174000"),
                            "registro_funcional": "1234567",
                            "nome": "JOÃO DA SILVA",
                            "email": "joao.silva@email.com",
                            "telefone": "",
                            "celular": "11999999999",
                            "cargo": {
                                "codigo": "1",
                                "nome": "DIRETOR",
                            },
                            "ativo": True,
                            "criado_pelo_sincronizador": True,
                        },
                    ],
                },
            ),
        ],
    ),
)


SUBPREFEITURA = extend_schema_view(
    list=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Lista subprefeituras",
        description=(
            "Retorna a lista de subprefeituras cadastradas no sistema. "
            "Permite filtrar por código EOL e nome."
        ),
    ),
    retrieve=extend_schema(
        tags=[TAG_ESCOLA],
        summary="Obtém uma subprefeitura",
        description=("Retorna os dados de uma subprefeitura específica."),
    ),
)
