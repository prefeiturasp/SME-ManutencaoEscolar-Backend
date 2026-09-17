from unittest.mock import Mock

import pytest


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
