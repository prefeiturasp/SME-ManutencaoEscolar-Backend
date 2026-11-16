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
    nome_documento: serializers.CharField = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        write_only=True,
    )
    uuid_documento_exigido: serializers.UUIDField = serializers.UUIDField(
        source="documento_exigido.uuid", read_only=True, allow_null=True
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

    class Meta:
        """Configura os campos do documento da função profissional."""

        model = DocumentoFuncaoProfissional
        fields = (
            "uuid",
            "nome_documento",
            "uuid_documento_exigido",
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
        source="criado_por.username",
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
    cargo_alterado: serializers.SerializerMethodField = (
        serializers.SerializerMethodField()
    )
    documentos_exigidos: serializers.SerializerMethodField = (
        serializers.SerializerMethodField()
    )

    def get_documentos_exigidos(
        self, funcao: FuncaoProfissional | dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Lista os documentos exigidos no momento do vínculo com o cargo.

        Cada item traz o arquivo já anexado ao documento, quando houver. A
        lista não muda quando o cadastro do cargo é alterado depois.

        Args:
            funcao: Função profissional que está sendo serializada.

        Returns:
            Documentos exigidos da função, em ordem de exibição.
        """
        if isinstance(funcao, dict):
            return list(funcao.get("documentos_exigidos", []))
        anexos = {
            anexo.documento_exigido_id: anexo
            for anexo in funcao.documentos.all()
            if anexo.documento_exigido_id is not None
        }
        return [
            {
                "uuid": str(exigido.uuid),
                "nome": exigido.nome,
                "ordem": exigido.ordem,
                "documento": (
                    DocumentoFuncaoProfissionalSerializer(
                        anexos[exigido.id], context=self.context
                    ).data
                    if exigido.id in anexos
                    else None
                ),
            }
            for exigido in funcao.documentos_exigidos.all()
        ]

    def get_cargo_alterado(
        self, funcao: FuncaoProfissional | dict[str, Any]
    ) -> bool:
        """Informa se o cargo foi alterado após o vínculo com o profissional.

        A edição de um cargo (inclusive de seus documentos) sempre atualiza
        ``atualizado_em`` do cargo. Já a data do vínculo é ``criado_em`` da
        função, que só muda quando o cargo é removido e adicionado novamente.

        Args:
            funcao: Função profissional que está sendo serializada.

        Returns:
            True quando o cargo foi atualizado depois do vínculo.
        """
        if isinstance(funcao, dict):
            cargo, vinculado_em = funcao["cargo"], funcao["criado_em"]
        else:
            cargo, vinculado_em = funcao.cargo, funcao.criado_em
        return bool(cargo.atualizado_em > vinculado_em)

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
            "cargo_alterado",
            "documentos_exigidos",
            "documentos",
        )
