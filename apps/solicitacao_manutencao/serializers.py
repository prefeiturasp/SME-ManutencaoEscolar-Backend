"""Serializers do domínio de solicitações de manutenção."""

from typing import Any

from rest_framework import serializers

from apps.escola.models.unidade_educacional import Unidadeeducacional
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

    uuid: serializers.UUIDField = serializers.UUIDField(required=False)
    arquivo: serializers.FileField = serializers.FileField(required=False)

    class Meta:
        """Configura os campos da foto do reparo."""

        model = FotoLocalReparo
        fields = ("uuid", "arquivo")

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
