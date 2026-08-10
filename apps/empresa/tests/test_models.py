"""Testes para o modelo Empresa."""

from apps.empresa.models import Empresa


def test_str_do_empresa():
    """Testa o método __str__ do modelo Empresa."""
    empresa = Empresa(nome="Empresa Exemplo", cnpj="12345678901234")

    assert str(empresa) == "Empresa Exemplo - 12345678901234"
