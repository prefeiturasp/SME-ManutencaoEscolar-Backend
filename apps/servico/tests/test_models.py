"""Testes para o modelo Serviço."""

from apps.servico.models import Servico


def test_str_do_servico():
    """Testa o método __str__ do modelo Serviço."""
    servico = Servico(
        nome="Serviço de Jardinagem",
        status=True,
    )

    assert str(servico) == "Serviço de Jardinagem"
