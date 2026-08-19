"""Testes para os modelos da aplicação Empresa."""

from apps.empresa.models import Empresa, ResponsavelTecnico


def test_str_do_empresa():
    """Testa o método __str__ do modelo Empresa."""
    empresa = Empresa(nome="Empresa Exemplo", cnpj="12345678901234")

    assert str(empresa) == "Empresa Exemplo - 12345678901234"


def test_str_do_responsavel_tecnico():
    """Testa o método __str__ do modelo ResponsavelTecnico."""
    empresa = Empresa(nome="Empresa Exemplo", cnpj="12345678901234")
    responsavel = ResponsavelTecnico(nome="João Responsável", empresa=empresa)

    assert str(responsavel) == "João Responsável - Empresa Exemplo"
