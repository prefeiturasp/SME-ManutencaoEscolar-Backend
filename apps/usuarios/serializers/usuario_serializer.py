"""Serializers responsáveis pela representação dos dados de usuários.

Define os serializers utilizados para representar perfis de acesso e os dados
do usuário autenticado nas respostas da API.
"""

from rest_framework import serializers

from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.escola.serializers.unidade_educacional_serializers import (
    DadosUnidadeEducacionalSerializer,
    DiretoriaRegionalUnidadeEducacionalSerializer,
    LoteUnidadeEducacionalSerializer,
    SubprefeituraUnidadeEducacionalSerializer,
    TipoEscolaUnidadeEducacionalSerializer,
)
from apps.usuarios.constants import Funcionalidade


class PerfilSerializer(serializers.Serializer):
    """Representa um perfil de acesso."""

    codigo = serializers.CharField(
        help_text="Código do perfil de acesso.",
    )
    descricao = serializers.CharField(
        help_text="Descrição do perfil de acesso.",
    )


class PerfilAcessoSerializer(serializers.Serializer):
    """Representa o cargo e o perfil de acesso do usuário.

    Usuários sem cargo vinculado possuem o perfil de acesso vazio.
    """

    cargo = serializers.CharField(
        required=False,
        help_text="Nome do cargo do usuário. Ausente quando não há cargo.",
    )
    perfil = PerfilSerializer(required=False)


class UnidadeEducacionalLoginSerializer(serializers.ModelSerializer):
    """Representa os dados da escola na resposta do login."""

    diretoria_regional = DiretoriaRegionalUnidadeEducacionalSerializer(
        read_only=True,
    )
    tipo_escola = TipoEscolaUnidadeEducacionalSerializer(read_only=True)
    subprefeitura = SubprefeituraUnidadeEducacionalSerializer(
        read_only=True,
    )
    lote = LoteUnidadeEducacionalSerializer(read_only=True)
    dados = DadosUnidadeEducacionalSerializer(read_only=True)

    class Meta:
        model = Unidadeeducacional
        fields = (
            "id",
            "uuid",
            "codigo_eol",
            "nome",
            "diretoria_regional",
            "tipo_escola",
            "subprefeitura",
            "lote",
            "status",
            "dados",
        )
        read_only_fields = fields


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
    funcionalidades = serializers.ListField(
        child=serializers.ChoiceField(choices=Funcionalidade.choices),
        help_text="Funcionalidades liberadas para o perfil do usuário.",
    )
    diretoria_regional = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        help_text="Diretoria Regional de Educação do usuário.",
    )
    unidade_educacional = UnidadeEducacionalLoginSerializer(
        allow_null=True,
        read_only=True,
    )
