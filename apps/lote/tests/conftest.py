import pytest

from apps.escola.models.diretoria_regional import DiretoriaRegional


@pytest.fixture
def diretoria_regional_nova():
    """Cria uma  Diretoria Regional para testes."""
    return DiretoriaRegional.objects.create(
        codigo="DRE02",
        nome="DIRETORIA REGIONAL DE EDUCACAO SUL",
        abreviacao="SUL",
    )
