"""Testes do model DadosUnidadeEducacional."""

import pytest
from django.db import IntegrityError

from apps.escola.models import DadosUnidadeEducacional

pytestmark = pytest.mark.django_db


class TestDadosUnidadeEducacional:
    """Testes do model DadosUnidadeEducacional."""

    def test_deve_criar_dados_da_unidade_educacional_com_dados_validos(
        self,
        unidade_educacional_emef,
    ):
        """Deve criar os dados da unidade com os dados informados."""
        dados = DadosUnidadeEducacional.objects.create(
            unidade_educacional=unidade_educacional_emef,
            email="escola@email.com",
            telefone="1122223333",
            logradouro="RUA TAPERA",
            numero="415",
            bairro="VILA NOVA CURUCA",
            cep="08032450",
            municipio="SAO PAULO",
            uf="SP",
        )

        assert dados.unidade_educacional == unidade_educacional_emef
        assert dados.email == "escola@email.com"
        assert dados.telefone == "1122223333"
        assert dados.logradouro == "RUA TAPERA"
        assert dados.numero == "415"
        assert dados.bairro == "VILA NOVA CURUCA"
        assert dados.cep == "08032450"
        assert dados.municipio == "SAO PAULO"
        assert dados.uf == "SP"

    def test_deve_permitir_criar_dados_com_campos_vazios(
        self,
        unidade_educacional_emef,
    ):
        """Deve permitir criar dados com campos opcionais vazios."""
        dados = DadosUnidadeEducacional.objects.create(
            unidade_educacional=unidade_educacional_emef,
        )

        assert dados.email == ""
        assert dados.telefone == ""
        assert dados.logradouro == ""
        assert dados.numero == ""
        assert dados.bairro == ""
        assert dados.cep == ""
        assert dados.municipio == ""
        assert dados.uf == ""

    def test_deve_acessar_dados_pelo_relacionamento_da_unidade(
        self,
        unidade_educacional_emef,
    ):
        """Deve acessar os dados através do relacionamento da unidade."""
        dados = DadosUnidadeEducacional.objects.create(
            unidade_educacional=unidade_educacional_emef,
            email="escola@email.com",
            telefone="1122223333",
            logradouro="RUA TAPERA",
            numero="415",
            bairro="VILA NOVA CURUCA",
            cep="08032450",
            municipio="SAO PAULO",
            uf="SP",
        )

        assert unidade_educacional_emef.dados == dados

    def test_nao_deve_permitir_dois_dados_para_mesma_unidade(
        self,
        unidade_educacional_emef,
    ):
        """Não deve permitir dois registros para a mesma unidade."""
        DadosUnidadeEducacional.objects.create(
            unidade_educacional=unidade_educacional_emef,
            email="primeiro@email.com",
        )

        with pytest.raises(IntegrityError):
            DadosUnidadeEducacional.objects.create(
                unidade_educacional=unidade_educacional_emef,
                email="segundo@email.com",
            )

    def test_deve_representar_dados_da_unidade_com_str(
        self,
        unidade_educacional_emef,
    ):
        """Deve retornar a unidade na representação textual."""
        dados = DadosUnidadeEducacional(
            unidade_educacional=unidade_educacional_emef,
        )

        assert str(dados) == (f"Dados de {unidade_educacional_emef}")

    def test_deve_excluir_dados_ao_excluir_unidade(
        self,
        unidade_educacional_emef,
    ):
        """Deve excluir os dados quando a unidade for excluída."""
        DadosUnidadeEducacional.objects.create(
            unidade_educacional=unidade_educacional_emef,
            email="escola@email.com",
        )

        unidade_educacional_emef.delete()

        assert not DadosUnidadeEducacional.objects.exists()

    def test_deve_permitir_atualizar_dados_da_unidade(
        self,
        unidade_educacional_emef,
    ):
        """Deve permitir atualizar os dados existentes."""
        dados = DadosUnidadeEducacional.objects.create(
            unidade_educacional=unidade_educacional_emef,
            email="antigo@email.com",
            telefone="11111111",
            logradouro="RUA ANTIGA",
            numero="100",
            bairro="BAIRRO ANTIGO",
            cep="01000000",
            municipio="SAO PAULO",
            uf="SP",
        )

        dados.email = "novo@email.com"
        dados.telefone = "22222222"
        dados.logradouro = "RUA NOVA"
        dados.numero = "200"
        dados.bairro = "BAIRRO NOVO"
        dados.cep = "02000000"
        dados.municipio = "SAO PAULO"
        dados.uf = "SP"
        dados.save()

        dados.refresh_from_db()

        assert dados.email == "novo@email.com"
        assert dados.telefone == "22222222"
        assert dados.logradouro == "RUA NOVA"
        assert dados.numero == "200"
        assert dados.bairro == "BAIRRO NOVO"
        assert dados.cep == "02000000"
        assert dados.municipio == "SAO PAULO"
        assert dados.uf == "SP"
