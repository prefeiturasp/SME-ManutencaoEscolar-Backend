"""Serializers de Autenticação."""

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
    access_expires_in = serializers.IntegerField(
        help_text="Tempo de validade do token de acesso em segundos.",
    )
    refresh_expires_in = serializers.IntegerField(
        help_text="Tempo de validade do token de atualização em segundos.",
    )
    usuario = UsuarioResponseSerializer()


class AtualizarTokenSerializer(serializers.Serializer):
    """Valida os dados da requisição de atualização de token."""

    refresh = serializers.CharField(
        required=True,
        help_text="Refresh token JWT obtido durante a autenticação do "
        "usuário. Será utilizado para gerar um novo access token.",
    )


class LogoutSerializer(serializers.Serializer):
    """Valida os dados da requisição de logout do sistema."""

    refresh = serializers.CharField(
        required=True,
        help_text="Refresh token JWT que será revogado durante o processo de "
        "logout. Após a revogação, o token não poderá mais ser utilizado para "
        "obter novos access tokens.",
    )


class RecuperarSenhaSerializer(serializers.Serializer):
    """Valida os dados da requisição de recuperação de senha."""

    registro_funcional_ou_cpf = serializers.CharField(
        required=True,
        max_length=11,
        trim_whitespace=True,
        help_text="Registro funcional ou CPF do usuário.",
    )


class AlterarSenhaSerializer(serializers.Serializer):
    """Valida os dados da requisição de alteração de senha."""

    registro_funcional_ou_cpf = serializers.CharField(
        required=True,
        min_length=7,
        max_length=11,
        trim_whitespace=True,
        help_text="RF ou CPF do usuário para redefinição de senha.",
    )
    token = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Token de recuperação de senha enviado por e-mail.",
    )
    senha = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Nova senha do usuário.",
    )
    confirmacao_senha = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Confirmação da nova senha do usuário.",
    )

    def validate_registro_funcional_ou_cpf(self, value: str) -> str:
        if len(value) not in {7, 11}:
            raise serializers.ValidationError(
                "O registro_funcional_ou_cpf deve ser um RF com 7 dígitos ou "
                "um CPF com 11 dígitos."
            )

        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["senha"] != attrs["confirmacao_senha"]:
            raise serializers.ValidationError(
                {"confirmacao_senha": "As senhas não coincidem."}
            )

        return attrs
