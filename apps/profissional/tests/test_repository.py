"""Testes dos repositórios do domínio Profissional."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.constants import TipoArquivo
from apps.profissional.models import (
    DocumentoFuncaoProfissional,
    FuncaoProfissional,
    Profissional,
)
from apps.profissional.repository.documento_funcao_repository import (
    DocumentoFuncaoProfissionalRepository,
)
from apps.profissional.repository.funcao_profissional_repository import (
    FuncaoProfissionalRepository,
)
from apps.profissional.repository.profissional_repository import (
    ProfissionalRepository,
)

pytestmark = pytest.mark.django_db


def test_profissional_repository_cria(usuario_ativo):
    """Persiste um profissional."""
    repository = ProfissionalRepository()
    resultado = repository.criar(
        {
            "nome": "José da Silva",
            "cpf": "12345678901",
            "rg": "123456789",
            "criado_por": usuario_ativo,
        }
    )
    profissional = Profissional.objects.get(pk=resultado["id"])

    assert resultado["nome"] == profissional.nome
    assert resultado["uuid"] == str(profissional.uuid)
    assert profissional.criado_por == usuario_ativo


def test_funcao_repository_cria(cargo_profissional, usuario_ativo):
    """Persiste uma função profissional."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    repository = FuncaoProfissionalRepository()

    funcao = repository.criar(
        {
            "profissional": profissional,
            "cargo": cargo_profissional,
            "criado_por": usuario_ativo,
        }
    )
    funcao_persistida = FuncaoProfissional.objects.get(pk=funcao["id"])
    assert funcao["uuid"] == str(funcao_persistida.uuid)
    assert funcao_persistida.criado_por == usuario_ativo


def test_documento_repository_cria(cargo_profissional, usuario_ativo):
    """Persiste um documento de função."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    repository = DocumentoFuncaoProfissionalRepository()
    arquivo = SimpleUploadedFile(
        "NR10.pdf", b"conteudo", content_type="application/pdf"
    )

    documento = repository.criar(
        {
            "nome_original": "NR10.pdf",
            "arquivo": arquivo,
            "tipo": TipoArquivo.DOCUMENTO,
            "tipo_mime": "application/pdf",
            "tamanho_bytes": len(b"conteudo"),
            "funcao_profissional": funcao,
            "criado_por": usuario_ativo,
        }
    )
    documento_persistido = DocumentoFuncaoProfissional.objects.get(
        pk=documento["id"]
    )
    assert documento["uuid"] == str(documento_persistido.uuid)
    assert documento["nome_original"] == documento_persistido.nome_original
    assert documento["tipo"] == documento_persistido.tipo
    assert documento["tipo_mime"] == documento_persistido.tipo_mime
    assert documento["tamanho_bytes"] == documento_persistido.tamanho_bytes
    assert documento_persistido.criado_por == usuario_ativo
