"""Testes do model HistoricoResponsavel."""

import pytest
from django.db import IntegrityError

from apps.escola.models import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)

pytestmark = pytest.mark.django_db


class TestHistoricoResponsavel:
    """Testes do model HistoricoResponsavel."""

    def test_deve_criar_historico_com_dados_validos(
        self,
        unidade_educacional_emef,
        cargo_perfil_diretor,
    ):
        """Deve criar um histórico com os dados informados."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
        )

        historico = HistoricoResponsavel.objects.create(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
            ativo=True,
        )

        assert historico.responsavel == responsavel
        assert historico.unidade_educacional == unidade_educacional_emef
        assert historico.cargo == cargo_perfil_diretor
        assert historico.ativo is True

    def test_atual_deve_retornar_true_quando_ativo(self):
        """Deve indicar que o vínculo está atual quando ativo."""
        historico = HistoricoResponsavel(ativo=True)

        assert historico.atual is True

    def test_atual_deve_retornar_false_quando_inativo(self):
        """Deve indicar que o vínculo não está atual quando inativo."""
        historico = HistoricoResponsavel(ativo=False)

        assert historico.atual is False

    def test_deve_permitir_mesmo_responsavel_em_varias_escolas(
        self,
        unidade_educacional_emef,
        unidade_educacional_cemei,
        cargo_perfil_diretor,
    ):
        """Deve permitir o mesmo responsável em várias unidades."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
        )

        HistoricoResponsavel.objects.create(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
            ativo=True,
        )

        HistoricoResponsavel.objects.create(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_cemei,
            cargo=cargo_perfil_diretor,
            ativo=True,
        )

        assert responsavel.historicos_unidade.count() == 2
        assert responsavel.escolas_atuais.count() == 2

    def test_nao_deve_permitir_mesmo_vinculo_duplicado(
        self,
        unidade_educacional_emef,
        cargo_perfil_diretor,
    ):
        """Não deve permitir o mesmo vínculo mais de uma vez."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
        )

        HistoricoResponsavel.objects.create(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
            ativo=True,
        )

        with pytest.raises(IntegrityError):
            HistoricoResponsavel.objects.create(
                responsavel=responsavel,
                unidade_educacional=unidade_educacional_emef,
                cargo=cargo_perfil_diretor,
                ativo=True,
            )

    def test_deve_atualizar_vinculo_inativo_para_ativo(
        self,
        unidade_educacional_emef,
        cargo_perfil_diretor,
    ):
        """Deve permitir reativar um vínculo."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
        )

        historico = HistoricoResponsavel.objects.create(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
            ativo=False,
        )

        historico.ativo = True
        historico.save()

        historico.refresh_from_db()

        assert historico.ativo is True
        assert historico.atual is True

    def test_deve_registrar_datas_de_auditoria(
        self,
        unidade_educacional_emef,
        cargo_perfil_diretor,
    ):
        """Deve registrar criação e atualização automaticamente."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
        )

        historico = HistoricoResponsavel.objects.create(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
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
