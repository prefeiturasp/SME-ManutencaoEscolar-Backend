from unittest.mock import Mock

import pytest

from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models.cargo_eol import CargoEOL


@pytest.fixture
def resposta_api_cargos():
    """Retorna uma resposta simulada da API de cargos EOL."""
    resposta = Mock()
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = [
        {
            "codigoCargo": 1000,
            "nomeCargo": "ASSISTENTE ADMINISTRATIVO",
        },
        {
            "codigoCargo": 2000,
            "nomeCargo": "SUPERVISOR ESCOLAR",
        },
    ]
    return resposta


@pytest.fixture
def cargo_eol_coordenador() -> CargoEOL:
    """Fixture de cargo de coordenador de UE."""
    return CargoEOL.objects.create(
        codigo="99999",
        nome="CARGO COORDENADOR",
        perfil=PerfilAcesso.UE,
        ativo=True,
    )
