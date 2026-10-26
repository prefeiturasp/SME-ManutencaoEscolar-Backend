"""Serializers utilizados para autenticação e recuperação de senha."""

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
        """Valida o tamanho do identificador utilizado no login.

        O valor deve possuir exatamente 7 dígitos, correspondente ao RF,
        ou 11 dígitos, correspondente ao CPF.

        Args:
            value (str): Identificador informado para autenticação.

        Raises:
            serializers.ValidationError: Se o identificador não possuir 7 ou
                11 caracteres.

        Returns:
            str: Identificador validado.
        """
        if len(value) not in {7, 11}:
            raise serializers.ValidationError(
                "O login deve ser um RF com 7 dígitos ou um CPF com 11 "
                "dígitos."
            )
        return value


class LoginResponseSerializer(serializers.Serializer):
    """Serializa a resposta retornada após uma autenticação bem-sucedida.

    A resposta contém os tokens JWT, seus respectivos tempos de validade
    e os dados do usuário autenticado.
    """

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
    """Valida os dados utilizados na atualização de um token JWT.

    Recebe o refresh token utilizado pelo fluxo de renovação da autenticação.
    """

    refresh = serializers.CharField(
        required=True,
        help_text="Refresh token JWT obtido durante a autenticação do "
        "usuário. Será utilizado para gerar um novo access token.",
    )


class LogoutSerializer(serializers.Serializer):
    """Valida os dados da requisição de logout do sistema.

    Recebe o refresh token que será validado e posteriormente revogado
    durante o processo de logout.
    """

    refresh = serializers.CharField(
        required=True,
        help_text="Refresh token JWT que será revogado durante o processo de "
        "logout. Após a revogação, o token não poderá mais ser utilizado para "
        "obter novos access tokens.",
    )


class RecuperarSenhaSerializer(serializers.Serializer):
    """Valida os dados da requisição de recuperação de senha.

    Recebe o registro funcional ou CPF utilizado para identificar o usuário
    que deverá receber as instruções de recuperação de senha.

    """

    registro_funcional_ou_cpf = serializers.CharField(
        required=True,
        max_length=11,
        trim_whitespace=True,
        help_text="Registro funcional ou CPF do usuário.",
    )


class AlterarSenhaSerializer(serializers.Serializer):
    """Valida os dados da requisição para redefinir a senha do usuário.

    Recebe o identificador do usuário, o token de recuperação e a nova senha.
    Também verifica se a confirmação da senha corresponde à nova senha
    informada.
    """

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
        """Valida o tamanho do identificador do usuário.

        O valor deve possuir exatamente 7 dígitos, correspondente ao RF,
        ou 11 dígitos, correspondente ao CPF.

        Args:
            value (str): Registro funcional ou CPF informado.

        Raises:
            serializers.ValidationError:  Se o identificador não possuir
                7 ou 11 caracteres.

        Returns:
            str: Identificador validado.
        """
        if len(value) not in {7, 11}:
            raise serializers.ValidationError(
                "O registro_funcional_ou_cpf deve ser um RF com 7 dígitos ou "
                "um CPF com 11 dígitos."
            )

        return value

    def validate(self, attrs: dict) -> dict:
        """Valida a correspondência entre a senha e sua confirmação.

        Args:
            attrs (dict): Dados já validados individualmente pelo serializer.

        Raises:
            serializers.ValidationError: Se ``senha`` e ``confirmacao_senha``
                forem diferentes.

        Returns:
            dict: Dados validados.
        """
        if attrs["senha"] != attrs["confirmacao_senha"]:
            raise serializers.ValidationError(
                {"confirmacao_senha": "As senhas não coincidem."}
            )

        return attrs
