"""Serializer do app usuarios."""

from rest_framework import serializers


class PerfilSerializer(serializers.Serializer):
    """Representa um perfil de acesso."""

    codigo = serializers.CharField(
        help_text="Código do perfil de acesso.",
    )
    descricao = serializers.CharField(
        help_text="Descrição do perfil de acesso.",
    )


class PerfilAcessoSerializer(serializers.Serializer):
    """Representa o cargo e o perfil de acesso do usuário."""

    cargo = serializers.CharField(
        help_text="Nome do cargo do usuário.",
    )
    perfil = PerfilSerializer()


class UsuarioResponseSerializer(serializers.Serializer):
    """Representa os dados do usuário autenticado."""

    id = serializers.IntegerField(help_text="Identificador do usuário.")
    uuid = serializers.UUIDField(help_text="Identificador único do usuário.")
    nome = serializers.CharField(help_text="Nome completo do usuário.")
    email = serializers.EmailField(help_text="E-mail do usuário.")
    registro_funcional = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Registro Funcional (RF) do usuário.",
    )
    cpf = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="CPF do usuário.",
    )
    username = serializers.CharField(
        help_text="Nome de usuário utilizado na autenticação."
    )
    perfil_acesso = PerfilAcessoSerializer()
    diretoria_regional = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        help_text="Diretoria Regional de Educação do usuário.",
    )
    unidade_educacional = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        help_text="Unidade Educacional do usuário.",
    )
