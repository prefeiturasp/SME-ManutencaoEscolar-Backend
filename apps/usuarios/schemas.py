"""Esquemas OpenAPI para os endpoints de usuarios."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)

from apps.usuarios.serializers.usuario_serializer import (
    UsuarioResponseSerializer,
)

ME = extend_schema(
    tags=["Usuario"],
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
