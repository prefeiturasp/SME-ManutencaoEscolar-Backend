"""Testes do repository de Unidade Educacional."""

import pytest

from apps.escola.repository import UnidadeEducacionalRepository

pytestmark = pytest.mark.django_db


class TestUnidadeEducacionalRepository:
    """Testa as operações de persistência da unidade educacional."""

    def test_deve_buscar_responsavel_por_registro_funcional(
        self,
        responsavel_unidade,
    ):
        """Deve localizar responsável pelo registro funcional."""
        resultado = (
            UnidadeEducacionalRepository().buscar_por_registro_funcional(
                responsavel_unidade.registro_funcional,
            )
        )

        assert resultado == responsavel_unidade

    def test_deve_retornar_none_quando_registro_funcional_nao_existir(
        self,
    ):
        """Deve retornar None quando o RF não existir."""
        resultado = (
            UnidadeEducacionalRepository().buscar_por_registro_funcional(
                "9999999",
            )
        )

        assert resultado is None

    def test_deve_verificar_vinculo_ativo(
        self,
        unidade_educacional_emef,
        historico_responsavel,
    ):
        """Deve identificar vínculo ativo do responsável."""
        resultado = UnidadeEducacionalRepository().existe_vinculo_ativo(
            unidade=unidade_educacional_emef,
            responsavel_uuid=historico_responsavel.responsavel.uuid,
        )

        assert resultado is True

    def test_deve_retornar_false_para_vinculo_inexistente(
        self,
        unidade_educacional_emef,
        responsavel_unidade,
    ):
        """Deve retornar False quando não houver vínculo ativo."""
        resultado = UnidadeEducacionalRepository().existe_vinculo_ativo(
            unidade=unidade_educacional_emef,
            responsavel_uuid=responsavel_unidade.uuid,
        )

        assert resultado is False

    def test_deve_atualizar_dados_da_unidade(
        self,
        unidade_educacional_emef,
        dados_unidade_emef,
        usuario_sincronizacao,
        historico_responsavel,
    ):
        """Deve atualizar status e dados de contato da unidade."""
        dados = {
            "email": "atualizado@email.com",
            "telefone": "1133334444",
            "ativo": False,
        }

        resultado = UnidadeEducacionalRepository().atualizar(
            unidade=unidade_educacional_emef,
            dados=dados,
            responsaveis=[],
            usuario=usuario_sincronizacao,
        )

        unidade_educacional_emef.refresh_from_db()
        dados_unidade_emef.refresh_from_db()

        assert unidade_educacional_emef.status is False
        assert dados_unidade_emef.email == "atualizado@email.com"
        assert dados_unidade_emef.telefone == "1133334444"
        assert resultado["id"] == unidade_educacional_emef.id

    def test_deve_atualizar_responsavel_existente(
        self,
        unidade_educacional_emef,
        dados_unidade_emef,
        historico_responsavel,
        usuario_sincronizacao,
    ):
        """Deve atualizar os dados do responsável existente."""
        responsavel = historico_responsavel.responsavel

        dados = {
            "email": "unidade@email.com",
            "telefone": "1133334444",
            "ativo": True,
        }

        responsaveis = [
            {
                "uuid": responsavel.uuid,
                "registro_funcional": responsavel.registro_funcional,
                "nome": "Nome Atualizado",
                "cargo": historico_responsavel.cargo.codigo,
                "email": "responsavel@email.com",
                "telefone": "1144445555",
                "celular": "11988887777",
            },
        ]

        UnidadeEducacionalRepository().atualizar(
            unidade=unidade_educacional_emef,
            dados=dados,
            responsaveis=responsaveis,
            usuario=usuario_sincronizacao,
        )

        responsavel.refresh_from_db()

        assert responsavel.nome == "Nome Atualizado"
        assert responsavel.email == "responsavel@email.com"
        assert responsavel.telefone == "1144445555"
        assert responsavel.celular == "11988887777"

    def test_deve_criar_novo_responsavel(
        self,
        unidade_educacional_emef,
        usuario_sincronizacao,
        cargo_perfil_diretor,
    ):
        """Deve criar responsável e seu vínculo com a unidade."""
        dados = {
            "email": "unidade@email.com",
            "telefone": "1133334444",
            "ativo": True,
        }

        responsaveis = [
            {
                "registro_funcional": "7654321",
                "nome": "Novo Responsável",
                "cargo": cargo_perfil_diretor.codigo,
                "email": "novo@email.com",
                "telefone": "",
                "celular": "",
            },
        ]

        UnidadeEducacionalRepository().atualizar(
            unidade=unidade_educacional_emef,
            dados=dados,
            responsaveis=responsaveis,
            usuario=usuario_sincronizacao,
        )

        from apps.escola.models.responsavel_unidade import (
            HistoricoResponsavel,
            ResponsavelUnidade,
        )

        responsavel = ResponsavelUnidade.objects.get(
            registro_funcional="7654321",
        )

        assert responsavel.nome == "Novo Responsável"
        assert responsavel.email == "novo@email.com"

        assert HistoricoResponsavel.objects.filter(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
            ativo=True,
        ).exists()
