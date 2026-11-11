"""Serializers da aplicação Empresa."""

from pathlib import Path
from typing import Any

from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from apps.core.constants import TAMANHO_MAXIMO_ARQUIVO
from apps.core.exceptions import (
    CepInvalidoError,
    CnpjInvalidoError,
    LinkRastreioInvalidoError,
)
from apps.core.validacoes import (
    validar_formato_cep,
    validar_formato_cnpj,
    validar_formato_link_rastreio,
)
from apps.empresa.constants import (
    LOGO_ASSINATURAS,
    LOGO_EXTENSOES_PERMITIDAS,
    EmpresaErrorMessages,
)
from apps.empresa.models import Empresa
from apps.empresa.serializers.anexo_serializers import ArquivoUploadField
from apps.empresa.serializers.responsavel_serializers import (
    ResponsavelTecnicoSerializer,
)
from apps.usuarios.models import Usuario


def obter_url_logo(empresa: Empresa | dict[str, Any]) -> str | None:
    """Retorna a URL da logo da empresa, quando houver.

    Args:
        empresa: Instância da empresa ou seus dados serializados.

    Returns:
        URL de acesso à logo ou ``None`` se a empresa não possuir logo.
    """
    logo = empresa.get("logo") if isinstance(empresa, dict) else empresa.logo
    return str(logo.url) if logo else None


class EmpresaSerializer(serializers.ModelSerializer):
    """Serializa a empresa para listagem e detalhes."""

    logo_url = serializers.SerializerMethodField()

    def get_logo_url(self, empresa: Empresa) -> str | None:
        """Retorna a URL de acesso à logo da empresa."""
        return obter_url_logo(empresa)

    criado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    atualizado_por: serializers.SlugRelatedField[Usuario] = (
        serializers.SlugRelatedField(slug_field="nome", read_only=True)
    )
    responsaveis_tecnicos: ResponsavelTecnicoSerializer = (
        ResponsavelTecnicoSerializer(many=True, read_only=True)
    )

    class Meta:
        """Configuração do serializer de empresa."""

        model = Empresa
        fields = (
            "id",
            "uuid",
            "nome",
            "cnpj",
            "status",
            "razao_social",
            "link_rastreio",
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "cidade",
            "estado",
            "logo_url",
            "criado_por",
            "criado_em",
            "atualizado_por",
            "atualizado_em",
            "responsaveis_tecnicos",
        )


class EmpresaCriarAtualizarSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de empresas."""

    responsaveis_tecnicos: ResponsavelTecnicoSerializer = (
        ResponsavelTecnicoSerializer(many=True)
    )
    logo = ArquivoUploadField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text=(
            "Imagem PNG, JPG ou JPEG de até 2 MB. Envie vazio/nulo na "
            "edição para remover a logo atual."
        ),
    )
    logo_url = serializers.SerializerMethodField()

    def get_logo_url(self, empresa: Empresa | dict[str, Any]) -> str | None:
        """Retorna a URL de acesso à logo da empresa."""
        return obter_url_logo(empresa)

    class Meta:
        """Configuração do serializer de empresa."""

        model = Empresa
        fields = (
            "nome",
            "cnpj",
            "razao_social",
            "status",
            "link_rastreio",
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "cidade",
            "estado",
            "logo",
            "logo_url",
            "responsaveis_tecnicos",
        )

    def validate_logo(self, value: UploadedFile | None) -> UploadedFile | None:
        """Valida extensão, tamanho e conteúdo da imagem da logo.

        Args:
            value: Arquivo enviado ou ``None`` para remover a logo.

        Returns:
            O arquivo validado ou ``None``.

        Raises:
            serializers.ValidationError: Se o formato, o tamanho ou o
                conteúdo do arquivo forem inválidos.
        """
        if value is None:
            return None
        extensao = Path(value.name or "").suffix.lower().lstrip(".")
        if extensao not in LOGO_EXTENSOES_PERMITIDAS:
            raise serializers.ValidationError(
                EmpresaErrorMessages.LOGO_FORMATO_INVALIDO
            )
        if (value.size or 0) > TAMANHO_MAXIMO_ARQUIVO:
            raise serializers.ValidationError(
                EmpresaErrorMessages.LOGO_MUITO_GRANDE
            )
        cabecalho = value.read(8)
        value.seek(0)
        if not cabecalho.startswith(LOGO_ASSINATURAS):
            raise serializers.ValidationError(
                EmpresaErrorMessages.LOGO_CONTEUDO_INVALIDO
            )
        return value

    def validate_cnpj(self, value: str) -> str:
        """Valida o formato do CNPJ informado."""
        try:
            validar_formato_cnpj(value)
        except CnpjInvalidoError:
            raise serializers.ValidationError(
                EmpresaErrorMessages.CNPJ_INVALIDO
            ) from None

        return value

    def validate_cep(self, value: str) -> str:
        """Garante que o CEP contenha apenas dígitos e tenha 8 caracteres."""
        try:
            validar_formato_cep(value)
        except CepInvalidoError:
            raise serializers.ValidationError(
                EmpresaErrorMessages.CEP_INVALIDO
            ) from None
        return value

    def validate_link_rastreio(self, value: str) -> str:
        """Garante que o link de rastreio seja uma URL válida."""
        if value:
            try:
                validar_formato_link_rastreio(value)
            except LinkRastreioInvalidoError:
                raise serializers.ValidationError(
                    EmpresaErrorMessages.LINK_RASTREIO_INVALIDO
                ) from None
        return value

    def validate_responsaveis_tecnicos(
        self, value: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Valida a lista de responsáveis técnicos.

        Exige ao menos um responsável e proíbe mais de um do mesmo ``tipo``
        no payload.
        """
        if len(value) < 1:
            raise serializers.ValidationError(
                EmpresaErrorMessages.RESPONSAVEL_TECNICO_OBRIGATORIO
            )
        tipos = [item["tipo"] for item in value]
        if len(tipos) != len(set(tipos)):
            raise serializers.ValidationError(
                EmpresaErrorMessages.RESPONSAVEL_TECNICO_TIPO_DUPLICADO
            )
        return value
