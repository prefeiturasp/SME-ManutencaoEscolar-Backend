"""Testes para os modelos da aplicação Empresa."""

from types import SimpleNamespace

import pytest

from apps.empresa.models import (
    AnexoResponsavelTecnico,
    Empresa,
    ResponsavelTecnico,
)


def test_str_do_empresa():
    """Testa o método __str__ do modelo Empresa."""
    empresa = Empresa(nome="Empresa Exemplo", cnpj="12345678901234")

    assert str(empresa) == "Empresa Exemplo - 12345678901234"


def test_str_do_responsavel_tecnico():
    """Testa o método __str__ do modelo ResponsavelTecnico."""
    empresa = Empresa(nome="Empresa Exemplo", cnpj="12345678901234")
    responsavel = ResponsavelTecnico(
        nome="João Responsável", tipo="preposto", empresa=empresa
    )

    assert str(responsavel) == "João Responsável - Preposto"


def test_str_do_anexo_responsavel_tecnico():
    """Testa o método __str__ do anexo do responsável técnico."""
    responsavel = ResponsavelTecnico(nome="João Responsável")
    anexo = AnexoResponsavelTecnico(responsavel_tecnico=responsavel)

    assert str(anexo) == "Anexo de João Responsável"


@pytest.mark.parametrize("nome_arquivo", [None, ""])
def test_nome_bucket_rejeita_nome_inexistente(nome_arquivo: str | None):
    """Verifica se rejeita arquivo sem nome definido."""
    anexo = AnexoResponsavelTecnico()
    anexo.arquivo = SimpleNamespace(name=nome_arquivo)

    with pytest.raises(
        ValueError, match="O nome do arquivo não está definido."
    ):
        _ = anexo.nome_bucket


def test_nome_bucket_retorna_nome_do_arquivo():
    """Verifica se retorna o nome do arquivo armazenado no bucket."""
    anexo = AnexoResponsavelTecnico()
    anexo.arquivo = SimpleNamespace(name="empresas/anexos/documento.pdf")

    assert anexo.nome_bucket == "empresas/anexos/documento.pdf"


def test_url_retorna_url_do_arquivo():
    """Verifica se retorna a URL fornecida pelo armazenamento."""
    anexo = AnexoResponsavelTecnico()
    anexo.arquivo = SimpleNamespace(
        url="https://minio.local/empresas/anexos/documento.pdf"
    )

    assert anexo.url == "https://minio.local/empresas/anexos/documento.pdf"
