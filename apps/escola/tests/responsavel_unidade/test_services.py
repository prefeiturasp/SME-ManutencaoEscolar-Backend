"""Testes do service de responsáveis da Unidade Educacional."""

import pytest
from rest_framework.exceptions import ValidationError

from apps.escola.repository.responsavel_unidade_repository import (
    ResponsavelUnidadeRepository,
)
from apps.escola.services.responsavel_unidade_service import (
    ResponsavelUnidadeService,
)

pytestmark = pytest.mark.django_db


class TestResponsavelUnidadeService:
    """Testa as regras de negócio dos responsáveis."""

    def test_deve_ignorar_responsavel_criado_pelo_sincronizador(self):
        """Não deve validar RF de responsável criado pelo sincronizador."""
        repository = ResponsavelUnidadeRepository()

        service = ResponsavelUnidadeService(
            repository=repository,
        )

        responsaveis = [
            {
                "registro_funcional": "0000011",
                "criado_pelo_sincronizador": True,
            },
        ]

        service.validar_registros_funcionais(
            responsaveis=responsaveis,
        )

    def test_deve_permitir_rf_que_nao_existe(self):
        """Deve permitir RF que ainda não esteja cadastrado."""
        repository = ResponsavelUnidadeRepository()

        service = ResponsavelUnidadeService(
            repository=repository,
        )

        service.validar_registros_funcionais(
            responsaveis=[
                {
                    "registro_funcional": "7654321",
                },
            ],
        )

    def test_deve_permitir_rf_do_proprio_responsavel(
        self,
        responsavel_unidade,
    ):
        """Deve permitir que o responsável mantenha seu próprio RF."""
        repository = ResponsavelUnidadeRepository()

        service = ResponsavelUnidadeService(
            repository=repository,
        )

        service.validar_registros_funcionais(
            responsaveis=[
                {
                    "uuid": str(responsavel_unidade.uuid),
                    "registro_funcional": (
                        responsavel_unidade.registro_funcional
                    ),
                },
            ],
        )

    def test_deve_rejeitar_rf_ja_existente_em_outro_responsavel(
        self,
        responsavel_unidade,
    ):
        """Deve rejeitar RF que já pertença a outro responsável."""
        repository = ResponsavelUnidadeRepository()

        service = ResponsavelUnidadeService(
            repository=repository,
        )

        with pytest.raises(ValidationError) as exc_info:
            service.validar_registros_funcionais(
                responsaveis=[
                    {
                        "registro_funcional": (
                            responsavel_unidade.registro_funcional
                        ),
                    },
                ],
            )

        assert (
            exc_info.value.detail["title"]
            == "Não é possível adicionar o contato"
        )
        assert (
            responsavel_unidade.registro_funcional
            in exc_info.value.detail["message"]
        )

    def test_deve_permitir_responsavel_sem_uuid(
        self,
        unidade_educacional_emef,
    ):
        """Deve ignorar validação de vínculo para responsável novo."""
        repository = ResponsavelUnidadeRepository()

        service = ResponsavelUnidadeService(
            repository=repository,
        )

        service.validar_responsaveis_da_unidade(
            unidade=unidade_educacional_emef,
            responsaveis=[
                {
                    "registro_funcional": "7654321",
                },
            ],
        )

    def test_deve_permitir_responsavel_com_vinculo_ativo(
        self,
        unidade_educacional_emef,
        historico_responsavel,
    ):
        """Deve permitir responsável que possui vínculo ativo."""
        repository = ResponsavelUnidadeRepository()

        service = ResponsavelUnidadeService(
            repository=repository,
        )

        service.validar_responsaveis_da_unidade(
            unidade=unidade_educacional_emef,
            responsaveis=[
                {
                    "uuid": str(historico_responsavel.responsavel.uuid),
                    "registro_funcional": (
                        historico_responsavel.responsavel.registro_funcional
                    ),
                },
            ],
        )

    def test_deve_rejeitar_responsavel_sem_vinculo_ativo(
        self,
        unidade_educacional_emef,
        responsavel_unidade,
    ):
        """Deve rejeitar responsável que não pertence à unidade."""
        repository = ResponsavelUnidadeRepository()

        service = ResponsavelUnidadeService(
            repository=repository,
        )

        with pytest.raises(ValidationError) as exc_info:
            service.validar_responsaveis_da_unidade(
                unidade=unidade_educacional_emef,
                responsaveis=[
                    {
                        "uuid": str(responsavel_unidade.uuid),
                        "registro_funcional": (
                            responsavel_unidade.registro_funcional
                        ),
                    },
                ],
            )
        assert (
            exc_info.value.detail["title"]
            == "Não é possível adicionar o contato"
        )
        assert exc_info.value.detail["message"] == (
            "O contato com o CPF/RF "
            f"{responsavel_unidade.registro_funcional} não está "
            "vinculado à unidade educacional."
        )
