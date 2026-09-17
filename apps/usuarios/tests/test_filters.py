"""Testes dos filtros de cargos EOL."""

import pytest

from apps.usuarios.filters import CargoEOLFilter
from apps.usuarios.models.cargo_eol import CargoEOL

pytestmark = pytest.mark.django_db


class TestCargoEOLFilter:
    """Testa os filtros de cargos EOL."""

    def test_filtra_por_codigo(
        self,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        filtro = CargoEOLFilter(
            data={"codigo": cargo_perfil_diretor.codigo},
            queryset=CargoEOL.objects.all(),
        )

        assert list(filtro.qs) == [cargo_perfil_diretor]

    def test_filtra_por_nome(
        self,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        filtro = CargoEOLFilter(
            data={"nome": "cargo coordenador"},
            queryset=CargoEOL.objects.all(),
        )

        assert list(filtro.qs) == [cargo_eol_coordenador]

    def test_filtra_por_nome_parcial(
        self,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        filtro = CargoEOLFilter(
            data={"nome": "cargo"},
            queryset=CargoEOL.objects.all(),
        )

        assert len(list(filtro.qs)) == 1
        assert cargo_eol_coordenador in list(filtro.qs)

    def test_filtra_por_perfil(
        self,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        filtro = CargoEOLFilter(
            data={"perfil": cargo_eol_coordenador.perfil},
            queryset=CargoEOL.objects.all(),
        )

        assert cargo_eol_coordenador in list(filtro.qs)
        assert cargo_perfil_diretor in list(filtro.qs)

    def test_filtra_por_ativo(
        self,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        filtro = CargoEOLFilter(
            data={"ativo": True},
            queryset=CargoEOL.objects.all(),
        )

        assert len(list(filtro.qs)) == 11
        assert cargo_perfil_diretor in list(filtro.qs)
        assert cargo_eol_coordenador in list(filtro.qs)

    def test_filtro_sem_resultado(
        self,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        filtro = CargoEOLFilter(
            data={"codigo": "codigo-inexistente"},
            queryset=CargoEOL.objects.all(),
        )

        assert not filtro.qs.exists()
