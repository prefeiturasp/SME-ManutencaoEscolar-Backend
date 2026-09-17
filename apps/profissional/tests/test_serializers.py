"""Testes dos serializers do domínio Profissional."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.constants import TipoArquivo
from apps.profissional.constants import ProfissionalErrorMessages
from apps.profissional.models import Profissional
from apps.profissional.serializers.profissional_serializers import (
    ProfissionalCriarAtualizarSerializer,
    ProfissionalSerializer,
)

pytestmark = pytest.mark.django_db


def test_serializer_valida_e_converte_payload(profissional_payload):
    """Converte o UUID do cargo no model correspondente."""
    serializer = ProfissionalCriarAtualizarSerializer(
        data=profissional_payload
    )

    assert serializer.is_valid(), serializer.errors
    cargo_uuid = str(serializer.validated_data["funcoes"][0]["cargo"].uuid)
    assert cargo_uuid == profissional_payload["funcoes"][0]["uuid_cargo"]


def test_serializer_rejeita_lista_de_funcoes_vazia(profissional_payload):
    """Exige ao menos uma função no cadastro."""
    serializer = ProfissionalCriarAtualizarSerializer(
        data={**profissional_payload, "funcoes": []}
    )

    assert not serializer.is_valid()
    assert str(serializer.errors["funcoes"][0]) == (
        ProfissionalErrorMessages.FUNCAO_PROFISSIONAL_OBRIGATORIA
    )


def test_serializer_rejeita_funcoes_duplicadas(profissional_payload):
    """Impede o mesmo cargo de ser informado duas vezes."""
    funcao = profissional_payload["funcoes"][0]
    serializer = ProfissionalCriarAtualizarSerializer(
        data={**profissional_payload, "funcoes": [funcao, funcao]}
    )

    assert not serializer.is_valid()
    assert str(serializer.errors["funcoes"][0]) == (
        ProfissionalErrorMessages.FUNCAO_PROFISSIONAL_DUPLICADA
    )


def test_serializer_rejeita_cpf_duplicado(profissional_payload):
    """Impede CPF em uso por outro profissional ativo."""
    Profissional.objects.create(
        nome="Existente",
        cpf=profissional_payload["cpf"],
        rg="outro-rg",
    )
    serializer = ProfissionalCriarAtualizarSerializer(
        data=profissional_payload
    )

    assert not serializer.is_valid()
    assert str(serializer.errors["cpf"][0]) == (
        ProfissionalErrorMessages.PROFISSIONAL_CPF_JA_CADASTRADO
    )


def test_serializer_rejeita_rg_duplicado(profissional_payload):
    """Impede RG em uso por outro profissional ativo."""
    Profissional.objects.create(
        nome="Existente",
        cpf="10987654321",
        rg=profissional_payload["rg"],
    )
    serializer = ProfissionalCriarAtualizarSerializer(
        data=profissional_payload
    )

    assert not serializer.is_valid()
    assert str(serializer.errors["rg"][0]) == (
        ProfissionalErrorMessages.PROFISSIONAL_RG_JA_CADASTRADO
    )


def test_serializer_atualizacao_ignora_cpf_e_rg_da_propria_instancia(
    profissional_payload,
):
    """Permite manter CPF e RG do profissional durante a atualização."""
    profissional = Profissional.objects.create(
        nome="Existente",
        cpf=profissional_payload["cpf"],
        rg=profissional_payload["rg"],
    )
    serializer = ProfissionalCriarAtualizarSerializer(
        instance=profissional,
        data=profissional_payload,
    )

    assert serializer.is_valid(), serializer.errors


def test_serializer_de_leitura_inclui_funcao_e_documento(
    cargo_profissional, usuario_ativo
):
    """Serializa o agregado com autoria, função e documento."""
    profissional = Profissional.objects.create(
        nome="José",
        cpf="12345678901",
        rg="123456789",
        criado_por=usuario_ativo,
    )
    funcao = profissional.funcoes.create(cargo=cargo_profissional)
    funcao.documentos.create(
        nome_original="NR10.pdf",
        arquivo=SimpleUploadedFile("NR10.pdf", b"conteudo"),
        tipo=TipoArquivo.DOCUMENTO,
        tipo_mime="application/pdf",
        tamanho_bytes=len(b"conteudo"),
    )

    dados = ProfissionalSerializer(profissional).data

    assert dados["criado_por"] == usuario_ativo.nome
    assert dados["funcoes"][0]["nome_cargo"] == cargo_profissional.nome
    documento = dados["funcoes"][0]["documentos"][0]
    assert documento["nome_original"] == "NR10.pdf"
    assert documento["tipo"] == TipoArquivo.DOCUMENTO
    assert documento["tipo_mime"] == "application/pdf"
    assert documento["tamanho_bytes"] == len(b"conteudo")
