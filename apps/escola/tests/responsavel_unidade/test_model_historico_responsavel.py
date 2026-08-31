"""Testes do model HistoricoResponsavel."""

import pytest
from django.db import IntegrityError

from apps.escola.models import (
    HistoricoResponsavel,
)

pytestmark = pytest.mark.django_db


class TestHistoricoResponsavel:
    """Testes do model HistoricoResponsavel."""

    def test_deve_criar_historico_com_dados_validos(
        self,
        unidade_educacional_emef,
        obter_cargo_diretor,
        responsavel_unidade,
    ):
        """Deve criar um histórico com os dados informados."""
        historico = HistoricoResponsavel.objects.create(
            responsavel=responsavel_unidade,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=True,
        )

        assert historico.responsavel == responsavel_unidade
        assert historico.unidade_educacional == unidade_educacional_emef
        assert historico.cargo == obter_cargo_diretor
        assert historico.ativo is True
        assert list(unidade_educacional_emef.responsaveis_atuais) == [
            historico
        ]
        assert unidade_educacional_emef.diretor_atual == responsavel_unidade

    def test_deve_permitir_mesmo_responsavel_em_varias_escolas(
        self,
        unidade_educacional_emef,
        unidade_educacional_cemei,
        obter_cargo_diretor,
        responsavel_unidade,
    ):
        """Deve permitir o mesmo responsável em várias unidades."""
        HistoricoResponsavel.objects.create(
            responsavel=responsavel_unidade,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=True,
        )

        HistoricoResponsavel.objects.create(
            responsavel=responsavel_unidade,
            unidade_educacional=unidade_educacional_cemei,
            cargo=obter_cargo_diretor,
            ativo=True,
        )

        assert responsavel_unidade.historicos_unidade.count() == 2
        assert responsavel_unidade.escolas_atuais.count() == 2

    def test_nao_deve_permitir_mesmo_vinculo_duplicado(
        self,
        unidade_educacional_emef,
        obter_cargo_diretor,
        responsavel_unidade,
    ):
        """Não deve permitir o mesmo vínculo mais de uma vez."""
        HistoricoResponsavel.objects.create(
            responsavel=responsavel_unidade,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=True,
        )

        with pytest.raises(IntegrityError):
            HistoricoResponsavel.objects.create(
                responsavel=responsavel_unidade,
                unidade_educacional=unidade_educacional_emef,
                cargo=obter_cargo_diretor,
                ativo=True,
            )

    def test_deve_atualizar_vinculo_inativo_para_ativo(
        self,
        unidade_educacional_emef,
        obter_cargo_diretor,
        responsavel_unidade,
    ):
        """Deve permitir reativar um vínculo."""
        historico = HistoricoResponsavel.objects.create(
            responsavel=responsavel_unidade,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=False,
        )

        historico.ativo = True
        historico.save()

        historico.refresh_from_db()

        assert historico.ativo is True

    def test_deve_registrar_datas_de_auditoria(
        self,
        unidade_educacional_emef,
        obter_cargo_diretor,
        responsavel_unidade,
    ):
        """Deve registrar criação e atualização automaticamente."""
        historico = HistoricoResponsavel.objects.create(
            responsavel=responsavel_unidade,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=True,
        )

        assert historico.criado_em is not None
        assert historico.atualizado_em is not None

        criado_em = historico.criado_em

        historico.ativo = False
        historico.save()

        historico.refresh_from_db()

        assert historico.criado_em == criado_em
        assert historico.atualizado_em >= criado_em

    def test_diretor_atual_deve_retornar_none_quando_nao_houver_diretor(
        self,
        unidade_educacional_emef,
    ):
        """Deve retornar None quando a unidade não possuir diretor atual."""
        assert unidade_educacional_emef.diretor_atual is None

    def test_deve_retornar_string_com_status_ativo(
        self,
        unidade_educacional_emef,
        obter_cargo_diretor,
        responsavel_unidade,
    ):
        """Deve representar o histórico ativo corretamente."""
        historico = HistoricoResponsavel.objects.create(
            responsavel=responsavel_unidade,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=True,
        )

        assert str(historico) == (
            f"{unidade_educacional_emef.codigo_eol} - "
            f"{responsavel_unidade.nome} - "
            f"{obter_cargo_diretor.nome} (ativo)"
        )

    def test_deve_retornar_string_com_status_inativo(
        self,
        unidade_educacional_emef,
        obter_cargo_diretor,
        responsavel_unidade,
    ):
        """Deve representar o histórico inativo corretamente."""
        historico = HistoricoResponsavel.objects.create(
            responsavel=responsavel_unidade,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=False,
        )

        assert str(historico) == (
            f"{unidade_educacional_emef.codigo_eol} - "
            f"{responsavel_unidade.nome} - "
            f"{obter_cargo_diretor.nome} (inativo)"
        )
