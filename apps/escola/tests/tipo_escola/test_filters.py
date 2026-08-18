"""Testes dos filtros do app escola."""

import pytest

from apps.escola.filters import TipoEscolaFilter
from apps.escola.models import TipoEscola

pytestmark = pytest.mark.django_db


class TestTipoEscolaFilter:
    """Testes dos filtros de tipos de escola."""

    def test_deve_retornar_todos_os_registros_sem_filtro(
        self,
        tipos_escola,
    ):
        """Deve retornar todos os tipos quando nenhum filtro for informado."""
        filtro = TipoEscolaFilter(
            data={},
            queryset=TipoEscola.objects.all(),
        )

        assert list(filtro.qs) == list(TipoEscola.objects.order_by("sigla"))

    def test_deve_filtrar_por_sigla_exata(
        self,
        tipos_escola,
    ):
        """Deve retornar registros que contenham a sigla informada."""
        filtro = TipoEscolaFilter(
            data={"sigla": "EMEF"},
            queryset=TipoEscola.objects.all(),
        )

        resultados = list(filtro.qs)

        assert len(resultados) == 1
        assert resultados[0].sigla == "EMEF"

    def test_deve_filtrar_por_parte_da_sigla(
        self,
        tipos_escola,
    ):
        """Deve permitir filtrar por parte da sigla."""
        filtro = TipoEscolaFilter(
            data={"sigla": "EM"},
            queryset=TipoEscola.objects.all(),
        )

        resultados = list(filtro.qs)

        assert {tipo.sigla for tipo in resultados} == {
            "EMEF",
            "CEMEI",
        }

    def test_deve_filtrar_sigla_sem_diferenciar_maiusculas_e_minusculas(
        self,
        tipos_escola,
    ):
        """Deve realizar o filtro sem diferenciar maiúsculas e minúsculas."""
        filtro = TipoEscolaFilter(
            data={"sigla": "emef"},
            queryset=TipoEscola.objects.all(),
        )

        resultados = list(filtro.qs)

        assert len(resultados) == 1
        assert resultados[0].sigla == "EMEF"

    def test_deve_retornar_queryset_vazio_quando_sigla_nao_existir(
        self,
        tipos_escola,
    ):
        """Deve retornar vazio quando não houver correspondência."""
        filtro = TipoEscolaFilter(
            data={"sigla": "ABC"},
            queryset=TipoEscola.objects.all(),
        )

        assert not filtro.qs.exists()

    def test_deve_ignorar_filtro_sigla_vazio(
        self,
        tipos_escola,
    ):
        """Deve retornar todos os registros quando a sigla estiver vazia."""
        filtro = TipoEscolaFilter(
            data={"sigla": ""},
            queryset=TipoEscola.objects.all(),
        )

        assert filtro.qs.count() == 2
