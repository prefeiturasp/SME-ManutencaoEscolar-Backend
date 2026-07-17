"""Esquemas OpenAPI para os endpoints de autenticação."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)

LOGIN = extend_schema(
    tags=["Autenticação"],
    summary="Login do usuário",
    description="Autentica o usuário via CoreSSO e retorna token JWT",
    operation_id="autenticarUsuario",
    parameters=[],
    request={
        "application/json": {
            "type": "object",
            "required": ["login", "senha"],
            "properties": {
                "login": {
                    "type": "string",
                    "description": "RF (7 dígitos) ou CPF (11 dígitos) do "
                    "usuário",
                    "example": "1234567",
                },
                "senha": {
                    "type": "string",
                    "description": "Senha do sistema EOL/CoreSSO",
                    "format": "password",
                    "example": "********",
                },
            },
        }
    },
    responses={
        200: OpenApiResponse(
            description="Login realizado com sucesso",
            examples=[
                OpenApiExample(
                    "Sucesso",
                    value={
                        "token": "token",
                        "refresh": "refresh",
                        "usuario": {
                            "nome": "João Silva",
                            "rf_cpf": "1234567",
                            "email": "joao@email.com",
                            "perfil": "SME",
                        },
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Dados inválidos"),
        401: OpenApiResponse(description="Credenciais inválidas"),
        500: OpenApiResponse(description="Erro no servidor"),
    },
)
