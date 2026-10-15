"""Testes do repository de Unidade Educacional."""

import pytest

from apps.escola.models.responsavel_unidade import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)
from apps.escola.repository.unidade_educacional_repository import (
    UnidadeEducacionalRepository,
)

pytestmark = pytest.mark.django_db


class TestUnidadeEducacionalRepository:
    """Testa as operações de persistência da unidade educacional."""

    def test_deve_buscar_responsavel_por_registro_funcional(
        self,
        historico_responsavel,
    ):
        """Deve localizar responsável pelo registro funcional."""
        responsavel_unidade = historico_responsavel.responsavel
        unidade = historico_responsavel.unidade_educacional

        resultado = (
            UnidadeEducacionalRepository().buscar_por_registro_funcional(
                responsavel_unidade.registro_funcional,
            )
        )

        assert resultado is not None
        assert resultado["uuid"] == str(responsavel_unidade.uuid)
        assert (
            resultado["registro_funcional"]
            == responsavel_unidade.registro_funcional
        )
        assert resultado["nome"] == responsavel_unidade.nome
        assert resultado["unidades"] == [
            {
                "id": unidade.id,
                "uuid": str(unidade.uuid),
                "codigo_eol": unidade.codigo_eol,
                "nome": unidade.nome,
            }
        ]

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

        UnidadeEducacionalRepository().atualizar(
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

    def test_deve_rejeitar_cargo_eol_inexistente(self):
        """Deve lançar erro quando o cargo EOL não existir."""
        codigo = "999999"

        with pytest.raises(
            ValueError,
            match=f"Cargo EOL com código {codigo} não encontrado.",
        ):
            UnidadeEducacionalRepository._obter_cargo(codigo)

    def test_deve_inativar_responsavel_que_nao_foi_enviado(
        self,
        unidade_educacional_emef,
        dados_unidade_emef,
        historico_responsavel,
        cargo_perfil_diretor,
        usuario_ativo,
    ):
        """Deve inativar o responsável que não foi enviado na atualização."""
        responsavel_mantido = historico_responsavel.responsavel
        responsavel_removido = ResponsavelUnidade.objects.create(
            registro_funcional="7654321",
            nome="Responsável Removido",
            email="removido@email.com",
            telefone="11999999999",
            celular="11988888888",
            criado_por=usuario_ativo,
            atualizado_por=usuario_ativo,
        )

        historico_removido = HistoricoResponsavel.objects.create(
            responsavel=responsavel_removido,
            unidade_educacional=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
            ativo=True,
        )

        dados = {
            "email": "unidade@email.com",
            "telefone": "1133334444",
            "ativo": True,
        }

        responsaveis = [
            {
                "uuid": str(responsavel_mantido.uuid),
                "registro_funcional": responsavel_mantido.registro_funcional,
                "nome": responsavel_mantido.nome,
                "cargo": historico_responsavel.cargo.codigo,
                "email": responsavel_mantido.email,
                "telefone": responsavel_mantido.telefone,
                "celular": responsavel_mantido.celular,
            },
        ]

        UnidadeEducacionalRepository().atualizar(
            unidade=unidade_educacional_emef,
            dados=dados,
            responsaveis=responsaveis,
            usuario=usuario_ativo,
        )

        historico_responsavel.refresh_from_db()
        historico_removido = HistoricoResponsavel.dm_objects.get(
            pk=historico_removido.pk,
        )

        assert historico_responsavel.ativo is True
        assert historico_responsavel.deletado_em is None

        assert historico_removido.ativo is False
        assert historico_removido.deletado_em is not None
        assert historico_removido.deletado_por == usuario_ativo
