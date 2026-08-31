"""Testes dos filtros de diretorias regionais."""

import pytest

from apps.escola.filters import DiretoriaRegionalFilter
from apps.escola.models.diretoria_regional import DiretoriaRegional

pytestmark = pytest.mark.django_db


class TestDiretoriaRegionalFilter:
    """Testa os filtros de diretorias regionais."""

    def test_filtra_por_codigo(
        self, diretoria_regional_centro, diretoria_regional_ipiranga
    ):
        filtro = DiretoriaRegionalFilter(
            data={"codigo": "DRE01"},
            queryset=DiretoriaRegional.objects.all(),
        )

        assert list(filtro.qs) == [diretoria_regional_centro]

    def test_filtra_por_nome_centro(
        self, diretoria_regional_centro, diretoria_regional_ipiranga
    ):
        filtro = DiretoriaRegionalFilter(
            data={"nome": "centro"},
            queryset=DiretoriaRegional.objects.all(),
        )

        assert list(filtro.qs) == [diretoria_regional_centro]

    def test_filtra_por_nome_diretoria(
        self, diretoria_regional_centro, diretoria_regional_ipiranga
    ):
        filtro = DiretoriaRegionalFilter(
            data={"nome": "diretoria"},
            queryset=DiretoriaRegional.objects.all(),
        )

        assert len(list(filtro.qs)) == 2
        assert diretoria_regional_centro in list(filtro.qs)
        assert diretoria_regional_ipiranga in list(filtro.qs)

    def test_filtra_por_abreviacao(
        self, diretoria_regional_centro, diretoria_regional_ipiranga
    ):
        filtro = DiretoriaRegionalFilter(
            data={"abreviacao": "ct"},
            queryset=DiretoriaRegional.objects.all(),
        )

        assert list(filtro.qs) == [diretoria_regional_centro]

    def test_filtro_sem_resultado(
        self, diretoria_regional_centro, diretoria_regional_ipiranga
    ):
        filtro = DiretoriaRegionalFilter(
            data={"codigo": "DRE"},
            queryset=DiretoriaRegional.objects.all(),
        )

        assert not filtro.qs.exists()
