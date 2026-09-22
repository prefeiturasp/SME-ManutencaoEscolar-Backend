"""Serializers de UnidadeEducacional."""

from rest_framework import serializers

from apps.escola.models.diretoria_regional import DiretoriaRegional
from apps.escola.models.responsavel_unidade import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)
from apps.escola.models.subprefeitura import Subprefeitura
from apps.escola.models.tipos_escola import TipoEscola
from apps.escola.models.unidade_educacional import (
    DadosUnidadeEducacional,
    Unidadeeducacional,
)
from apps.lote.models import Lote
from apps.usuarios.models.cargo_eol import CargoEOL


class TipoEscolaUnidadeEducacionalSerializer(serializers.ModelSerializer):
    """Serializa os dados do tipo de escola."""

    class Meta:
        model = TipoEscola
        fields = (
            "uuid",
            "sigla",
        )


class DiretoriaRegionalUnidadeEducacionalSerializer(
    serializers.ModelSerializer
):
    """Serializa os dados resumidos da diretoria regional."""

    class Meta:
        model = DiretoriaRegional
        fields = (
            "id",
            "nome_curto",
        )


class SubprefeituraUnidadeEducacionalSerializer(serializers.ModelSerializer):
    """Serializa os dados das subprefeituras."""

    class Meta:
        model = Subprefeitura
        fields = (
            "uuid",
            "nome",
        )


class LoteUnidadeEducacionalSerializer(serializers.ModelSerializer):
    """Serializa o lote associado à unidade educacional."""

    class Meta:
        model = Lote
        fields = (
            "uuid",
            "nome",
        )


class DadosUnidadeEducacionalSerializer(serializers.ModelSerializer):
    """Serializa os dados de contato e endereço da unidade educacional."""

    class Meta:
        model = DadosUnidadeEducacional
        fields = (
            "email",
            "telefone",
            "logradouro",
            "numero",
            "bairro",
            "cep",
            "municipio",
            "uf",
        )


class ResponsavelUnidadeSerializer(serializers.ModelSerializer):
    """Serializa os dados de um responsável da unidade."""

    class Meta:
        model = ResponsavelUnidade
        fields = (
            "registro_funcional",
            "nome",
            "email",
            "telefone",
            "celular",
        )


class CargoResponsavelUnidadeSerializer(serializers.ModelSerializer):
    """Serializa os dados do cargo exercido pelo responsável."""

    class Meta:
        model = CargoEOL
        fields = (
            "codigo",
            "nome",
        )


class ResponsavelAtualUnidadeSerializer(serializers.ModelSerializer):
    """Serializa um vínculo atual de responsável com a unidade."""

    uuid = serializers.UUIDField(
        source="responsavel.uuid",
        read_only=True,
    )
    registro_funcional = serializers.CharField(
        source="responsavel.registro_funcional",
        read_only=True,
    )
    nome = serializers.CharField(
        source="responsavel.nome",
        read_only=True,
    )
    email = serializers.EmailField(
        source="responsavel.email",
        read_only=True,
    )
    telefone = serializers.CharField(
        source="responsavel.telefone",
        read_only=True,
    )
    celular = serializers.CharField(
        source="responsavel.celular",
        read_only=True,
    )
    cargo = CargoResponsavelUnidadeSerializer(read_only=True)

    criado_pelo_sincronizador = serializers.SerializerMethodField()

    class Meta:
        model = HistoricoResponsavel
        fields = (
            "uuid",
            "registro_funcional",
            "nome",
            "email",
            "telefone",
            "celular",
            "cargo",
            "ativo",
            "criado_pelo_sincronizador",
        )

    def get_criado_pelo_sincronizador(
        self,
        obj: HistoricoResponsavel,
    ) -> bool:
        """Indica se o responsável foi criado pelo usuário sincronizador."""
        return (
            obj.responsavel.criado_por is not None
            and obj.responsavel.criado_por.username == "sincronizacao_eol"
        )


class UnidadeEducacionalSerializer(serializers.ModelSerializer):
    """Serializa os dados das unidades educacionais e seus relacionamentos."""

    diretoria_regional = DiretoriaRegionalUnidadeEducacionalSerializer(
        read_only=True
    )
    tipo_escola = TipoEscolaUnidadeEducacionalSerializer(read_only=True)
    subprefeitura = SubprefeituraUnidadeEducacionalSerializer(read_only=True)
    lote = LoteUnidadeEducacionalSerializer(read_only=True)
    dados = DadosUnidadeEducacionalSerializer(read_only=True)
    responsaveis = ResponsavelAtualUnidadeSerializer(
        source="responsaveis_atuais",
        many=True,
        read_only=True,
    )

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
            "responsaveis",
        )


class UnidadeEducacionalListSerializer(
    serializers.ModelSerializer,
):
    """Serializa unidades educacionais para listagem."""

    tipo_escola = TipoEscolaUnidadeEducacionalSerializer(read_only=True)

    diretoria_regional = DiretoriaRegionalUnidadeEducacionalSerializer(
        read_only=True,
    )

    subprefeitura = SubprefeituraUnidadeEducacionalSerializer(read_only=True)

    lote = LoteUnidadeEducacionalSerializer(read_only=True)

    class Meta:
        model = Unidadeeducacional
        fields = (
            "uuid",
            "codigo_eol",
            "nome",
            "tipo_escola",
            "diretoria_regional",
            "subprefeitura",
            "lote",
            "status",
        )
