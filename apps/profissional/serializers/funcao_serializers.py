"""Serializers de funções profissionais."""

from typing import Any

from rest_framework import serializers

from apps.cargo.models import Cargo
from apps.profissional.models import (
    DocumentoFuncaoProfissional,
    FuncaoProfissional,
)
from apps.usuarios.models.usuario import Usuario


class DocumentoFuncaoProfissionalSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de documentos de funções profissionais."""

    uuid: serializers.UUIDField = serializers.UUIDField(required=False)
    arquivo: serializers.FileField = serializers.FileField(required=False)

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

    class Meta:
        """Configura os campos do documento da função profissional."""

        model = DocumentoFuncaoProfissional
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


class FuncaoProfissionalSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de funções profissionais."""

    uuid: serializers.UUIDField = serializers.UUIDField(required=False)
    nome_cargo: serializers.CharField = serializers.CharField(
        source="cargo.nome", read_only=True
    )
    uuid_cargo: serializers.SlugRelatedField[Cargo] = (
        serializers.SlugRelatedField(
            source="cargo", slug_field="uuid", queryset=Cargo.objects.all()
        )
    )
    documentos: DocumentoFuncaoProfissionalSerializer = (
        DocumentoFuncaoProfissionalSerializer(many=True, required=False)
    )
    criado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    registro_funcional: serializers.CharField = serializers.CharField(
        source="criado_por.registro_funcional",
        read_only=True,
    )
    atualizado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    atualizado_em: serializers.DateTimeField = serializers.DateTimeField(
        read_only=True
    )
    criado_em: serializers.DateTimeField = serializers.DateTimeField(
        read_only=True
    )

    class Meta:
        """Configuração do serializer de Função Profissional."""

        model = FuncaoProfissional
        fields = (
            "uuid",
            "nome_cargo",
            "uuid_cargo",
            "criado_por",
            "registro_funcional",
            "criado_em",
            "atualizado_por",
            "atualizado_em",
            "documentos",
        )
