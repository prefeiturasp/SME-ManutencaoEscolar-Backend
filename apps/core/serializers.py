"""Serializers da aplicação Core."""

from rest_framework import serializers

from apps.usuarios.serializers.usuario_serializer import (
    UsuarioResponseSerializer,
)


class AutenticacaoSerializer(serializers.Serializer):
    """
    Valida os dados enviados para autenticação no CoreSSO.

    O campo ``login`` aceita tanto o RF (7 dígitos) quanto o CPF
    (11 dígitos) do usuário. O campo ``senha`` é utilizado apenas para
    autenticação e não é retornado na resposta da API.
    """

    login = serializers.CharField(
        max_length=11,
        min_length=7,
        required=True,
        help_text="RF (7 dígitos) ou CPF (11 dígitos) do usuário.",
    )
    senha = serializers.CharField(
        write_only=True,
        min_length=3,
        required=True,
        help_text="Senha do sistema EOL/CoreSSO.",
    )

    def validate_login(self, value: str) -> str:
        if len(value) not in {7, 11}:
            raise serializers.ValidationError(
                "O login deve ser um RF com 7 dígitos ou um CPF com 11 "
                "dígitos."
            )
        return value


class LoginResponseSerializer(serializers.Serializer):
    """Resposta da autenticação."""

    refresh = serializers.CharField(help_text="Token JWT de atualização.")
    access = serializers.CharField(help_text="Token JWT de acesso.")
    dados_usuario = UsuarioResponseSerializer
