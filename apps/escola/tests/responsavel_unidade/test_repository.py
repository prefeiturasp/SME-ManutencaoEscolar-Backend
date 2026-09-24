"""Testes do repository de responsáveis da Unidade Educacional."""

import pytest

from apps.escola.models.responsavel_unidade import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)
from apps.escola.repository.responsavel_unidade_repository import (
    ResponsavelUnidadeRepository,
)

pytestmark = pytest.mark.django_db


class TestResponsavelUnidadeRepository:
    """Testa as operações de persistência dos responsáveis."""

    def test_deve_buscar_responsavel_por_registro_funcional(
        self,
        historico_responsavel,
    ):
        """Deve localizar responsável e suas unidades ativas pelo RF."""
        responsavel = historico_responsavel.responsavel
        unidade = historico_responsavel.unidade_educacional

        resultado = (
            ResponsavelUnidadeRepository().buscar_por_registro_funcional(
                responsavel.registro_funcional,
            )
        )

        assert resultado is not None
        assert resultado["uuid"] == str(responsavel.uuid)
        assert (
            resultado["registro_funcional"] == responsavel.registro_funcional
        )
        assert resultado["nome"] == responsavel.nome
        assert resultado["unidades"] == [
            {
                "id": unidade.id,
                "uuid": str(unidade.uuid),
                "codigo_eol": unidade.codigo_eol,
                "nome": unidade.nome,
            }
        ]

    def test_deve_ignorar_vinculos_inativos_ao_buscar_responsavel(
        self,
        responsavel_unidade,
        unidade_educacional_emef,
        obter_cargo_diretor,
    ):
        """Deve retornar somente unidades com vínculo ativo."""
        HistoricoResponsavel.objects.create(
            responsavel=responsavel_unidade,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=False,
        )

        resultado = (
            ResponsavelUnidadeRepository().buscar_por_registro_funcional(
                responsavel_unidade.registro_funcional,
            )
        )

        assert resultado is not None
        assert resultado["unidades"] == []

    def test_deve_retornar_none_quando_registro_funcional_nao_existir(
        self,
    ):
        """Deve retornar None quando o RF não existir."""
        resultado = (
            ResponsavelUnidadeRepository().buscar_por_registro_funcional(
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
        resultado = ResponsavelUnidadeRepository().existe_vinculo_ativo(
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
        resultado = ResponsavelUnidadeRepository().existe_vinculo_ativo(
            unidade=unidade_educacional_emef,
            responsavel_uuid=responsavel_unidade.uuid,
        )

        assert resultado is False

    def test_deve_buscar_vinculo_ativo(
        self,
        unidade_educacional_emef,
        historico_responsavel,
    ):
        """Deve retornar o vínculo ativo do responsável."""
        resultado = ResponsavelUnidadeRepository().buscar_vinculo_ativo(
            unidade=unidade_educacional_emef,
            responsavel_uuid=historico_responsavel.responsavel.uuid,
        )

        assert resultado == historico_responsavel
        assert resultado.responsavel == historico_responsavel.responsavel
        assert resultado.cargo == historico_responsavel.cargo

    def test_deve_criar_vinculo(
        self,
        responsavel_unidade,
        unidade_educacional_emef,
        cargo_perfil_diretor,
        usuario_sincronizacao,
    ):
        """Deve criar um vínculo ativo para o responsável."""
        resultado = ResponsavelUnidadeRepository().criar_vinculo(
            responsavel=responsavel_unidade,
            unidade=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
            usuario=usuario_sincronizacao,
        )

        assert resultado.pk is not None
        assert resultado.responsavel == responsavel_unidade
        assert resultado.unidade_educacional == unidade_educacional_emef
        assert resultado.cargo == cargo_perfil_diretor
        assert resultado.ativo is True
        assert resultado.criado_por == usuario_sincronizacao
        assert resultado.atualizado_por == usuario_sincronizacao

    def test_deve_listar_vinculos_ativos(
        self,
        historico_responsavel,
        responsavel_unidade,
        unidade_educacional_emef,
        obter_cargo_diretor,
    ):
        """Deve listar somente os vínculos ativos da unidade."""
        responsavel_inativo = ResponsavelUnidade.objects.create(
            registro_funcional="7654321",
            nome="Responsável Inativo",
            email="inativo@email.com",
            telefone="",
            celular="",
            esta_afastado=False,
        )

        historico_inativo = HistoricoResponsavel.objects.create(
            responsavel=responsavel_inativo,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=False,
        )

        resultado = ResponsavelUnidadeRepository().listar_vinculos_ativos(
            unidade=unidade_educacional_emef,
        )

        assert historico_responsavel in resultado
        assert historico_inativo not in resultado
        assert len(resultado) == 1
