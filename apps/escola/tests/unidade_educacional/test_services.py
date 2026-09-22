"""Testes do service de Unidade Educacional."""

import pytest
from rest_framework.exceptions import ValidationError

from apps.escola.repository import UnidadeEducacionalRepository
from apps.escola.services import UnidadeEducacionalService

pytestmark = pytest.mark.django_db


class TestUnidadeEducacionalService:
    """Testa as regras de negócio da unidade educacional."""

    def test_deve_atualizar_unidade(
        self,
        unidade_educacional_emef,
        usuario_sincronizacao,
        cargo_perfil_diretor,
    ):
        """Deve delegar a atualização ao repository."""
        repository = UnidadeEducacionalRepository()

        dados = {
            "email": "nova@email.com",
            "telefone": "1133334444",
            "ativo": True,
            "responsaveis": [
                {
                    "registro_funcional": "1234567",
                    "nome": "João",
                    "cargo": cargo_perfil_diretor.codigo,
                    "email": "joao@email.com",
                    "telefone": "",
                    "celular": "",
                },
            ],
        }

        service = UnidadeEducacionalService(
            repository=repository,
        )

        dados_atualizados = service.atualizar(
            unidade=unidade_educacional_emef,
            dados=dados,
            usuario=usuario_sincronizacao,
        )
        assert dados_atualizados["dados"]["email"] == dados["email"]

    def test_deve_rejeitar_rf_duplicado_na_mesma_requisicao(
        self,
        unidade_educacional_emef,
        usuario_sincronizacao,
        cargo_perfil_diretor,
    ):
        """Deve rejeitar RF duplicado no mesmo payload."""
        repository = UnidadeEducacionalRepository()

        dados = {
            "email": "nova@email.com",
            "telefone": "",
            "ativo": True,
            "responsaveis": [
                {
                    "registro_funcional": "1234567",
                    "nome": "João",
                    "cargo": cargo_perfil_diretor.codigo,
                    "email": "joao@email.com",
                    "telefone": "",
                    "celular": "",
                },
                {
                    "registro_funcional": "1234567",
                    "nome": "Maria",
                    "cargo": cargo_perfil_diretor.codigo,
                    "email": "maria@email.com",
                    "telefone": "",
                    "celular": "",
                },
            ],
        }

        service = UnidadeEducacionalService(
            repository=repository,
        )

        with pytest.raises(ValidationError):
            service.atualizar(
                unidade=unidade_educacional_emef,
                dados=dados,
                usuario=usuario_sincronizacao,
            )

    def test_deve_permitir_rf_do_proprio_responsavel(
        self,
        unidade_educacional_emef,
        historico_responsavel,
        usuario_sincronizacao,
        cargo_perfil_diretor,
    ):
        """Deve permitir manter o RF do próprio responsável."""
        repository = UnidadeEducacionalRepository()
        responsavel_unidade = historico_responsavel.responsavel
        registro_funcional = responsavel_unidade.registro_funcional

        dados = {
            "email": "nova@email.com",
            "telefone": "",
            "ativo": True,
            "responsaveis": [
                {
                    "uuid": responsavel_unidade.uuid,
                    "registro_funcional": (
                        responsavel_unidade.registro_funcional
                    ),
                    "nome": "Nome atualizado",
                    "cargo": cargo_perfil_diretor.codigo,
                    "email": "novo@email.com",
                    "telefone": "",
                    "celular": "",
                },
            ],
        }

        service = UnidadeEducacionalService(
            repository=repository,
        )

        resultado = service.atualizar(
            unidade=unidade_educacional_emef,
            dados=dados,
            usuario=usuario_sincronizacao,
        )

        assert resultado is not None
        responsavel_unidade.refresh_from_db()

        assert responsavel_unidade.registro_funcional == registro_funcional
