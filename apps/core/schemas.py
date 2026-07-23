"""Esquemas OpenAPI para os endpoints de autenticação."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)

from apps.core.serializers import (
    AutenticacaoSerializer,
    LoginResponseSerializer,
)

LOGIN = extend_schema(
    auth=[],
    tags=["Autenticação"],
    summary="Login do usuário",
    description="Autentica o usuário via CoreSSO e retorna token JWT.",
    operation_id="autenticarUsuario",
    request=AutenticacaoSerializer,
    responses={
        200: LoginResponseSerializer,
        400: OpenApiResponse(description="Dados inválidos"),
        401: OpenApiResponse(description="Credenciais inválidas"),
        503: OpenApiResponse(description="Instabilidade"),
        500: OpenApiResponse(description="Erro no servidor"),
    },
    examples=[
        OpenApiExample(
            name="Exemplo de autenticação",
            request_only=True,
            value={
                "login": "1234567",
                "senha": "********",
            },
        ),
        OpenApiExample(
            name="Login realizado com sucesso",
            response_only=True,
            value={
                "refresh": "<jwt-refresh>",
                "access": "<jwt-access>",
                "dados_usuario": {
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
            },
        ),
    ],
)
