"""Testes do repository de diretorias regionais."""

import pytest

from apps.escola.models import DiretoriaRegional
from apps.escola.repository.diretoria_regional_repository import (
    DiretoriaRegionalRepository,
)

pytestmark = pytest.mark.django_db


class TestDiretoriaRegionalRepository:
    def test_serializar_diretoria_regional(self):
        """Serializa os dados da diretoria regional."""
        diretoria = DiretoriaRegional.objects.create(
            codigo="DRE01",
            nome="DIRETORIA REGIONAL DE EDUCACAO CENTRO",
            abreviacao="DRE-C",
        )

        resultado = DiretoriaRegionalRepository.serializar(diretoria)

        assert resultado == {
            "id": diretoria.id,
            "codigo": "DRE01",
            "nome": "DIRETORIA REGIONAL DE EDUCACAO CENTRO",
            "abreviacao": "DRE-C",
            "nome_curto": "DRE CENTRO",
        }

    def test_serializar_diretoria_regional_nula(self):
        """Retorna None quando não há diretoria regional."""
        resultado = DiretoriaRegionalRepository.serializar(None)

        assert resultado is None
