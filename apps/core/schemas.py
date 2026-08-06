"""Esquemas OpenAPI para os endpoints de autenticação."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)

from apps.core.serializers import (
    AtualizarTokenSerializer,
    AutenticacaoSerializer,
    LoginResponseSerializer,
    LogoutSerializer,
)

TAG_AUTENTICACAO = "Autenticação"
REFRESH_JWT = "<jwt-refresh>"

LOGIN = extend_schema(
    auth=[],
    tags=[TAG_AUTENTICACAO],
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
                "refresh": REFRESH_JWT,
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


ATUALIZA_TOKEN = extend_schema(
    tags=[TAG_AUTENTICACAO],
    summary="Renovar tokens JWT",
    description="Atualiza o token do usuário e retorna token JWT.",
    operation_id="atualizaTokenUsuario",
    request=AtualizarTokenSerializer,
    responses={
        200: OpenApiResponse(description="Credenciais validas"),
        401: OpenApiResponse(
            description="Refresh token inválido, expirado, "
            "revogado ou associado a um usuário inexistente ou inativo."
        ),
    },
    examples=[
        OpenApiExample(
            name="Exemplo atualização de token",
            request_only=True,
            value={"refresh": REFRESH_JWT},
        ),
        OpenApiExample(
            name="Token atualizado com sucesso",
            response_only=True,
            status_codes=[200],
            value={
                "refresh": REFRESH_JWT,
                "access": "<jwt-access>",
            },
        ),
        OpenApiExample(
            name="Token inválido ou usuário inválido",
            response_only=True,
            status_codes=[401],
            value={"detail": "Mensagem"},
        ),
    ],
)


LOGOUT = extend_schema(
    tags=[TAG_AUTENTICACAO],
    summary="Realizar logout",
    description="Realiza o logout do usuário autenticado revogando o refresh"
    " token informado",
    operation_id="logoutUsuario",
    request=LogoutSerializer,
    responses={
        200: OpenApiResponse(
            description="Credenciais validasLogout realizado com sucesso"
        ),
        401: OpenApiResponse(
            description="Usuário autenticado inválido ou refresh token"
            "inválido, revogado ou não pertencente ao usuário autenticado."
        ),
    },
    examples=[
        OpenApiExample(
            name="Exemplo Logout",
            request_only=True,
            value={"refresh": REFRESH_JWT},
        ),
        OpenApiExample(
            name="Logout realizado com sucesso",
            response_only=True,
            status_codes=[205],
            value={
                "detail": "Logout realizado com sucesso.",
            },
        ),
        OpenApiExample(
            name="Refresh token inválido",
            response_only=True,
            status_codes=[401],
            value={
                "detail": ("O refresh token é inválido ou já foi revogado."),
            },
        ),
        OpenApiExample(
            name="Token não pertence ao usuário",
            response_only=True,
            status_codes=[401],
            value={
                "detail": ("O token não pertence ao usuário autenticado."),
            },
        ),
        OpenApiExample(
            name="Usuário autenticado inválido",
            response_only=True,
            status_codes=[401],
            value={
                "detail": "Usuário autenticado inválido.",
            },
        ),
    ],
)
