# apps/escola/tests/unidade_educacional/test_filters.py

"""Testes dos filtros de unidades educacionais."""

import pytest

from apps.escola.filters import UnidadeEducacionalFilter
from apps.escola.models.unidade_educacional import Unidadeeducacional

pytestmark = pytest.mark.django_db


class TestUnidadeEducacionalFilter:
    """Testa os filtros de unidades educacionais."""

    def test_filtra_por_codigo_eol(
        self, unidade_educacional_emef, unidade_educacional_cemei
    ):
        filtro = UnidadeEducacionalFilter(
            data={"codigo_eol": "100001"},
            queryset=Unidadeeducacional.objects.all(),
        )

        assert list(filtro.qs) == [unidade_educacional_emef]

    def test_filtra_por_tipo_escola(
        self,
        unidade_educacional_emef,
        tipo_escola_emef,
        unidade_educacional_cemei,
    ):
        filtro = UnidadeEducacionalFilter(
            data={"tipo_escola": str(tipo_escola_emef.uuid)},
            queryset=Unidadeeducacional.objects.all(),
        )

        assert list(filtro.qs) == [unidade_educacional_emef]

    def test_filtra_por_diretoria_regional(
        self,
        unidade_educacional_emef,
        diretoria_regional_centro,
        unidade_educacional_cemei,
    ):
        filtro = UnidadeEducacionalFilter(
            data={
                "diretoria_regional": diretoria_regional_centro.id,
            },
            queryset=Unidadeeducacional.objects.all(),
        )

        assert list(filtro.qs) == [unidade_educacional_emef]

    def test_filtra_por_unidade_educacional(
        self, unidade_educacional_emef, unidade_educacional_cemei
    ):
        filtro = UnidadeEducacionalFilter(
            data={
                "unidade_educacional": str(
                    unidade_educacional_emef.uuid,
                ),
            },
            queryset=Unidadeeducacional.objects.all(),
        )

        assert list(filtro.qs) == [unidade_educacional_emef]

    def test_filtra_por_subprefeitura(
        self,
        unidade_educacional_emef,
        subprefeitura_se,
        unidade_educacional_cemei,
    ):
        filtro = UnidadeEducacionalFilter(
            data={
                "subprefeitura": str(subprefeitura_se.uuid),
            },
            queryset=Unidadeeducacional.objects.all(),
        )

        assert list(filtro.qs) == [unidade_educacional_emef]

    def test_filtra_por_status_ativo(
        self, unidade_educacional_emef, unidade_educacional_inativa_emef
    ):
        filtro = UnidadeEducacionalFilter(
            data={"status": "true"},
            queryset=Unidadeeducacional.objects.all(),
        )

        assert list(filtro.qs) == [unidade_educacional_emef]

    def test_filtra_por_status_inativo(
        self,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
    ):
        filtro = UnidadeEducacionalFilter(
            data={"status": "false"},
            queryset=Unidadeeducacional.objects.all(),
        )

        assert list(filtro.qs) == [unidade_educacional_inativa_emef]

    def test_filtra_por_multiplos_campos(
        self,
        unidade_educacional_emef,
        tipo_escola_emef,
        diretoria_regional_centro,
        subprefeitura_se,
        unidade_educacional_inativa_emef,
    ):
        filtro = UnidadeEducacionalFilter(
            data={
                "tipo_escola": str(tipo_escola_emef.uuid),
                "diretoria_regional": diretoria_regional_centro.id,
                "subprefeitura": str(subprefeitura_se.uuid),
                "status": "true",
            },
            queryset=Unidadeeducacional.objects.all(),
        )

        assert list(filtro.qs) == [unidade_educacional_emef]

    def test_filtro_sem_resultado(
        self, unidade_educacional_emef, unidade_educacional_cemei
    ):
        filtro = UnidadeEducacionalFilter(
            data={"codigo_eol": "999999"},
            queryset=Unidadeeducacional.objects.all(),
        )

        assert not filtro.qs.exists()
