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


class FotoLocalReparoSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de documentos de funções profissionais."""

    uuid: serializers.UUIDField = serializers.UUIDField(required=False)
    arquivo: serializers.FileField = serializers.FileField(required=False)

    class Meta:
        """Configura os campos da foto do reparo."""

        model = FotoLocalReparo
        fields = (
            "uuid",
            "nome_original",
            "arquivo",
            "tipo",
            "tipo_mime",
            "tamanho_bytes",
        )
        read_only_fields = (
            "nome_original",
            "tipo",
            "tipo_mime",
            "tamanho_bytes",
        )

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


class ServicoManutencaoSerializer(serializers.ModelSerializer):
    """Valida um serviço durante a criação e atualização de uma solicitação."""

    servico = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Servico.objects.all(),
        required=False,
        allow_null=True,
        allow_empty=True,
    )
    servico_especifico = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    uuid = serializers.UUIDField(required=False)
    arquivos = FotoLocalReparoSerializer(
        many=True,
        required=True,
        allow_empty=False,
    )

    class Meta:
        """Configura os campos de criação do serviço."""

        model = ServicoManutencao
        fields = (
            "uuid",
            "servico",
            "servico_especifico",
            "local_reparo",
            "descricao",
            "arquivos",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Impede informar serviço catalogado e específico juntos.

        Args:
            attrs: Dados do serviço de manutenção.

        Returns:
            Dados validados do serviço de manutenção.

        Raises:
            serializers.ValidationError: Se as duas formas de serviço forem
                informadas simultaneamente.
        """
        if attrs.get("servico") == "":
            attrs["servico"] = None
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


class SolicitacaoManutencaoCriarEditarSerializer(serializers.ModelSerializer):
    """Valida e serializa a criação e atualização de uma solicitação."""

    unidade_educacional = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Unidadeeducacional.objects.all(),
        required=False,
    )
    servicos = ServicoManutencaoSerializer(many=True)

    class Meta:
        """Configura os campos de entrada da solicitação."""

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
            "uuid",
            "servico_uuid",
            "nome_servico",
            "servico_especifico",
            "local_reparo",
            "descricao",
            "arquivos",
        )
        read_only_fields = fields


class SolicitacaoManutencaoDetalheSerializer(serializers.ModelSerializer):
    """Serializa os dados completos de uma solicitação de manutenção."""

    unidade_educacional = serializers.SerializerMethodField()
    servicos = serializers.SerializerMethodField()

    def get_unidade_educacional(
        self, obj: dict[str, Any] | SolicitacaoManutencao
    ) -> dict[str, Any]:
        """Serializa a unidade educacional associada à solicitação."""
        unidade_id = (
            obj["unidade_educacional_id"]
            if isinstance(obj, dict)
            else obj.unidade_educacional_id
        )
        unidade = (
            Unidadeeducacional.objects.select_related(
                "diretoria_regional", "tipo_escola", "subprefeitura"
            )
            .prefetch_related("diretoria_regional__vinculo_lote__lote")
            .get(pk=unidade_id)
        )
        return UnidadeEducacionalSerializer(unidade).data

    def get_servicos(
        self, obj: dict[str, Any] | SolicitacaoManutencao
    ) -> list[dict[str, Any]]:
        """Serializa os serviços associados à solicitação."""
        solicitacao_id = obj["id"] if isinstance(obj, dict) else obj.id
        servicos = (
            ServicoManutencao.objects.select_related("servico")
            .prefetch_related("fotos")
            .filter(solicitacao_manutencao_id=solicitacao_id)
        )
        return cast(
            list[dict[str, Any]],
            ServicoManutencaoDetalhesSerializer(servicos, many=True).data,
        )

    class Meta:
        """Configura os campos exibidos da solicitação."""

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
