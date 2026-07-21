"""Testes para o modelo Fornecedor."""

from apps.fornecedor.models import Fornecedor


def test_str_do_fornecedor():
    """Testa o método __str__ do modelo Fornecedor."""
    fornecedor = Fornecedor(nome="Fornecedor Exemplo", cnpj="12345678901234")

    assert str(fornecedor) == "Fornecedor Exemplo - 12345678901234"
