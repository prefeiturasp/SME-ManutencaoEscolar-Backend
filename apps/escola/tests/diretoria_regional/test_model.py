"""Testes do model Unidadeeducacional."""

import pytest

from apps.escola.models import DiretoriaRegional

pytestmark = pytest.mark.django_db


class TestDiretoriaRegional:
    def test_str_do_dre(self):
        """Testa o método __str__ do modelo Dre."""
        dre = DiretoriaRegional(
            nome="Diretoria Exemplo", abreviacao="DRE", codigo="123"
        )

        assert str(dre) == "DRE - Diretoria Exemplo"

    def test_deve_retornar_nome_curto_para_nome_padrao(self):
        """Deve substituir o prefixo padrão por DRE."""
        diretoria = DiretoriaRegional(
            codigo="DRE01",
            nome="DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
            abreviacao="DRE-C",
        )

        assert diretoria.nome_curto == "DRE BUTANTA"

    def test_deve_retornar_nome_original_quando_nao_possuir_prefixo(self):
        """Deve retornar o nome original quando não houver o prefixo."""
        diretoria = DiretoriaRegional(
            codigo="DRE01",
            nome="DIRETORIA CENTRO",
            abreviacao="DRE-C",
        )

        assert diretoria.nome_curto == "DIRETORIA CENTRO"

    def test_deve_retornar_nome_original_quando_nome_for_vazio(self):
        """Deve retornar o nome vazio quando não houver nome."""
        diretoria = DiretoriaRegional(
            codigo="DRE01",
            nome="",
            abreviacao="DRE-C",
        )

        assert diretoria.nome_curto == ""

    def test_deve_criar_diretoria_regional(self):
        """Deve persistir uma Diretoria Regional corretamente."""
        diretoria = DiretoriaRegional.objects.create(
            codigo="DRE01",
            nome="DIRETORIA REGIONAL DE EDUCACAO CENTRO",
            abreviacao="DRE-C",
        )

        assert diretoria.pk is not None
        assert diretoria.codigo == "DRE01"
        assert diretoria.nome == "DIRETORIA REGIONAL DE EDUCACAO CENTRO"
        assert diretoria.abreviacao == "DRE-C"
