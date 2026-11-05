"""Serializers do domínio de solicitações de manutenção."""

from typing import Any, cast

from rest_framework import serializers

from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.escola.serializers.unidade_educacional_serializers import (
    UnidadeEducacionalSerializer,
)
from apps.servico.models import Servico
from apps.solicitacao_manutencao.models import (
    FotoLocalReparo,
    ServicoManutencao,
    SolicitacaoManutencao,
)


class SolicitacaoManutencaoListSerializer(serializers.ModelSerializer):
    """Serializa uma solicitação de manutenção para listagem."""

    class Meta:
        """Configura os campos exibidos na listagem de solicitações."""

        model = SolicitacaoManutencao
        fields = (
            "uuid",
            "codigo",
            "tipo_atendimento",
            "situacao",
            "data_envio",
            "fase",
        )


class FotoLocalReparoSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de documentos de funções profissionais."""

    class Meta:
        """Configura os campos da foto do reparo."""

        model = FotoLocalReparo
        fields = ("uuid", "arquivo", "nome_original")
        extra_kwargs = {
            "uuid": {"required": False},
            "arquivo": {"required": False},
        }
        read_only_fields = ("nome_original",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Exige arquivo apenas quando não há documento existente.

        Args:
            attrs: Dados do documento a serem validados.

        Returns:
            Dados validados do documento.
        """
        if not attrs.get("uuid") and not attrs.get("arquivo"):
            raise serializers.ValidationError(
                {"arquivo": self.fields["arquivo"].error_messages["required"]}
            )
        return attrs


class ServicoManutencaoCriarSerializer(serializers.ModelSerializer):
    """Valida um serviço durante a criação de uma solicitação."""

    servico = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Servico.objects.all(),
        required=False,
        allow_null=True,
    )
    arquivos = FotoLocalReparoSerializer(
        many=True,
        required=True,
        allow_empty=False,
    )

    class Meta:
        """Configura os campos de criação do serviço."""

        model = ServicoManutencao
        fields = (
            "servico",
            "servico_especifico",
            "local_reparo",
            "descricao",
            "arquivos",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Impede o envio conjunto de serviço e serviço específico.

        Args:
            attrs: Dados do serviço de manutenção.

        Returns:
            Dados validados do serviço de manutenção.

        Raises:
            serializers.ValidationError: Se um serviço catalogado e um
                serviço específico forem informados simultaneamente.
        """
        if attrs.get("servico") and attrs.get("servico_especifico"):
            raise serializers.ValidationError(
                {
                    "servico_especifico": (
                        "Não informe um serviço específico quando um serviço "
                        "catalogado for selecionado."
                    )
                }
            )
        return attrs


class SolicitacaoManutencaoCriarSerializer(serializers.ModelSerializer):
    """Valida e serializa a criação de uma solicitação."""

    unidade_educacional = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Unidadeeducacional.objects.all(),
    )
    servicos = ServicoManutencaoCriarSerializer(many=True)

    class Meta:
        """Configura os campos do cadastro da solicitação."""

        model = SolicitacaoManutencao
        fields = (
            "uuid",
            "codigo",
            "tipo_atendimento",
            "informacoes_adicionais",
            "unidade_educacional",
            "situacao",
            "data_envio",
            "fase",
            "servicos",
        )
        read_only_fields = ("uuid", "situacao", "data_envio", "fase", "codigo")

    def validate_servicos(
        self, value: list[dict[str, object]]
    ) -> list[dict[str, object]]:
        """Exige ao menos um serviço na solicitação."""
        if not value:
            raise serializers.ValidationError(
                "Informe ao menos um serviço de manutenção."
            )
        return value


class ServicoManutencaoDetalhesSerializer(serializers.ModelSerializer):
    """Serializa os dados de leitura de um serviço da solicitação."""

    arquivos = FotoLocalReparoSerializer(
        source="fotos", many=True, read_only=True
    )
    servico_uuid: serializers.SlugRelatedField = serializers.SlugRelatedField(
        source="servico", slug_field="uuid", read_only=True, allow_null=True
    )
    nome_servico = serializers.CharField(
        source="servico.nome", read_only=True, allow_null=True
    )

    class Meta:
        """Configura os campos exibidos do serviço de manutenção."""

        model = ServicoManutencao
        fields = (
            "servico_uuid",
            "nome_servico",
            "servico_especifico",
            "local_reparo",
            "descricao",
            "arquivos",
        )
        read_only_fields = fields


class SolicitacaoManutencaoDetalheSerializer(serializers.Serializer):
    """Serializa os dados completos de uma solicitação de manutenção."""

    def get_unidade_educacional(self, obj: dict[str, Any]) -> dict[str, Any]:
        """Serializa a unidade educacional associada à solicitação."""
        unidade = (
            Unidadeeducacional.objects.select_related(
                "diretoria_regional", "tipo_escola", "subprefeitura"
            )
            .prefetch_related("diretoria_regional__vinculo_lote__lote")
            .get(pk=obj["unidade_educacional_id"])
        )
        return UnidadeEducacionalSerializer(unidade).data

    def get_servicos(self, obj: dict[str, Any]) -> list[dict[str, Any]]:
        """Serializa os serviços associados à solicitação."""
        servicos = (
            ServicoManutencao.objects.select_related("servico")
            .prefetch_related("fotos")
            .filter(solicitacao_manutencao_id=obj["id"])
        )
        return cast(
            list[dict[str, Any]],
            ServicoManutencaoDetalhesSerializer(servicos, many=True).data,
        )

    uuid = serializers.UUIDField(read_only=True)
    unidade_educacional = serializers.SerializerMethodField()
    servicos = serializers.SerializerMethodField()
    codigo = serializers.CharField(read_only=True)
    tipo_atendimento = serializers.CharField(read_only=True)
    informacoes_adicionais = serializers.CharField(read_only=True)
    situacao = serializers.CharField(read_only=True)
    solicitante = serializers.CharField(read_only=True)
    data_envio = serializers.DateTimeField(read_only=True, allow_null=True)
    fase = serializers.CharField(read_only=True)
