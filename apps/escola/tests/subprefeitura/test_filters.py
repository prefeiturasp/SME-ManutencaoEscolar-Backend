"""Testes dos filtros de subprefeituras."""

import pytest

from apps.escola.filters import SubprefeituraFilter
from apps.escola.models.subprefeitura import Subprefeitura

pytestmark = pytest.mark.django_db


class TestSubprefeituraFilter:
    """Testa os filtros de subprefeituras."""

    def test_filtra_por_codigo_eol(
        self, subprefeitura_se, subprefeitura_pirituba
    ):
        filtro = SubprefeituraFilter(
            data={"codigo_eol": "SP01"},
            queryset=Subprefeitura.objects.all(),
        )

        assert list(filtro.qs) == [subprefeitura_se]

    def test_filtra_por_nome_case_insensitive(
        self, subprefeitura_se, subprefeitura_pirituba
    ):
        filtro = SubprefeituraFilter(
            data={"nome": "sé"},
            queryset=Subprefeitura.objects.all(),
        )

        assert list(filtro.qs) == [subprefeitura_se]

    def test_filtra_por_nome_parcial(
        self,
        subprefeitura_se,
        subprefeitura_pirituba,
    ):
        filtro = SubprefeituraFilter(
            data={"nome": "subprefeitura"},
            queryset=Subprefeitura.objects.all(),
        )

        assert len(list(filtro.qs)) == 2
        assert subprefeitura_se in list(filtro.qs)
        assert subprefeitura_pirituba in list(filtro.qs)

    def test_filtro_sem_resultado(
        self, subprefeitura_se, subprefeitura_pirituba
    ):
        filtro = SubprefeituraFilter(
            data={"codigo_eol": "999"},
            queryset=Subprefeitura.objects.all(),
        )

        assert not filtro.qs.exists()
