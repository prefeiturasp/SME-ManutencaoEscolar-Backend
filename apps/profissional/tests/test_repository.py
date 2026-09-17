"""Testes dos repositórios do domínio Profissional."""

import pytest

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

    documento = repository.criar(
        {
            "nome": "NR10",
            "funcao_profissional": funcao,
            "criado_por": usuario_ativo,
        }
    )
    documento_persistido = DocumentoFuncaoProfissional.objects.get(
        pk=documento["id"]
    )
    assert documento["uuid"] == str(documento_persistido.uuid)
    assert documento_persistido.criado_por == usuario_ativo
