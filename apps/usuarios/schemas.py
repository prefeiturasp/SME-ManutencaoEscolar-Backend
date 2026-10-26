"""Esquemas OpenAPI para os endpoints do app usuarios."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.usuarios.serializers.cargo_eol_serializer import (
    CargoEOLSerializer,
)
from apps.usuarios.serializers.usuario_serializer import (
    UsuarioResponseSerializer,
)

TAG_USUARIOS = "Usuários"

ME = extend_schema(
    tags=[TAG_USUARIOS],
    summary="Obter usuário autenticado",
    description=(
        "Retorna os dados do usuário autenticado a partir das "
        "informações presentes no token de autenticação."
    ),
    operation_id="obterUsuarioAutenticado",
    responses={
        200: UsuarioResponseSerializer,
        401: OpenApiResponse(
            description="Usuário não autenticado ou token inválido."
        ),
    },
    examples=[
        OpenApiExample(
            name="Login realizado com sucesso",
            response_only=True,
            value={
                "id": 1,
                "uuid": "2e7d7d7d-9b8b-4c92-9b3b-123456789abc",
                "nome": "Fulano da Silva",
                "email": "fulano@emial.com",
                "registro_funcional": "1234567",
                "cpf": "12345678901",
                "username": "1234567",
                "perfil_acesso": {
                    "cargo": "DIRETOR DE ESCOLA",
                    "perfil": {
                        "codigo": "UE",
                        "descricao": "Diretor Unidade Educacional",
                    },
                },
                "diretoria_regional": "DRE Exemplo",
                "unidade_educacional": "EMEF Exemplo",
            },
        ),
    ],
)


CARGO_EOL = extend_schema_view(
    list=extend_schema(
        tags=[TAG_USUARIOS],
        summary="Lista os cargos EOL",
        description=(
            "Retorna a lista paginada de cargos EOL cadastrados no sistema. "
            "Permite filtrar os cargos pelo código, nome, perfil de acesso "
            "e situação de atividade."
        ),
        operation_id="listarCargosEol",
        parameters=[
            OpenApiParameter(
                name="codigo",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=("Filtra pelo código exato do cargo EOL."),
                examples=[
                    OpenApiExample(
                        "Código do cargo",
                        value="3360",
                    ),
                ],
            ),
            OpenApiParameter(
                name="nome",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Filtra pelo nome do cargo. A pesquisa considera "
                    "correspondência parcial e não diferencia letras "
                    "maiúsculas de minúsculas."
                ),
                examples=[
                    OpenApiExample(
                        "Nome do cargo",
                        value="diretor",
                    ),
                ],
            ),
            OpenApiParameter(
                name="perfil",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Filtra pelo perfil de acesso associado ao cargo."
                ),
                examples=[
                    OpenApiExample(
                        "Perfil UE",
                        value="UE",
                    ),
                    OpenApiExample(
                        "Perfil DRE",
                        value="DRE",
                    ),
                    OpenApiExample(
                        "Perfil SME",
                        value="SME",
                    ),
                    OpenApiExample(
                        "Perfil Empresa",
                        value="EMPRESA",
                    ),
                ],
            ),
            OpenApiParameter(
                name="ativo",
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Filtra pela situação do cargo. Utilize `true` para "
                    "cargos ativos ou `false` para cargos inativos."
                ),
                examples=[
                    OpenApiExample(
                        "Cargos ativos",
                        value=True,
                    ),
                    OpenApiExample(
                        "Cargos inativos",
                        value=False,
                    ),
                ],
            ),
        ],
        responses={
            200: CargoEOLSerializer(many=True),
        },
    ),
    retrieve=extend_schema(
        tags=[TAG_USUARIOS],
        summary="Consulta um cargo EOL",
        description=(
            "Retorna os dados de um cargo EOL específico identificado pelo ID."
        ),
        operation_id="obterCargoEol",
        responses={
            200: CargoEOLSerializer,
            404: OpenApiResponse(
                description="Cargo EOL não encontrado",
            ),
        },
    ),
)
