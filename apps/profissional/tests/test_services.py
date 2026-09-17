"""Testes dos serviços do domínio Profissional."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError

from apps.profissional.constants import ProfissionalErrorMessages
from apps.profissional.services.documento_funcao_services import (
    DocumentoFuncaoProfissionalService,
)
from apps.profissional.services.funcao_profissional_services import (
    FuncaoProfissionalService,
)
from apps.profissional.services.profissional_services import (
    ProfissionalService,
)


def test_documento_service_cria_documentos():
    """Cria os documentos vinculados à função."""
    repository = MagicMock()
    service = DocumentoFuncaoProfissionalService(repository=repository)

    service.sincronizar(10, [{"nome": "Novo"}])

    repository.criar.assert_called_once_with(
        {"nome": "Novo", "funcao_profissional_id": 10, "criado_por": None}
    )


def test_funcao_service_cria_funcao_e_delega_documentos():
    """Cria uma função e delega a criação de seus documentos."""
    repository = MagicMock()
    documento_service = MagicMock()
    criada = {"id": 3}
    documentos_criados = [{"id": 4, "nome": "Novo"}]
    repository.criar.return_value = criada
    documento_service.sincronizar.return_value = documentos_criados
    cargo = SimpleNamespace(exige_documento=False)
    service = FuncaoProfissionalService(repository, documento_service)

    service.sincronizar(
        20,
        [{"cargo": cargo, "documentos": [{"nome": "Novo"}]}],
    )

    repository.criar.assert_called_once_with(
        {"cargo": cargo, "profissional_id": 20, "criado_por": None}
    )
    documento_service.sincronizar.assert_called_once_with(
        criada["id"], [{"nome": "Novo"}], None
    )
    assert criada["documentos"] == documentos_criados


def test_funcao_service_exige_documento_quando_configurado():
    """Impede função sem documento quando o cargo o exige."""
    repository = MagicMock()
    service = FuncaoProfissionalService(repository, MagicMock())
    funcoes = [{"cargo": SimpleNamespace(exige_documento=True)}]

    with pytest.raises(ValidationError) as exc_info:
        service.sincronizar(20, funcoes)

    assert exc_info.value.message_dict == {
        "documentos": [
            ProfissionalErrorMessages.DOCUMENTOS_FUNCAO_PROFISSIONAL_OBRIGATORIOS
        ]
    }
    repository.criar.assert_not_called()


@pytest.mark.django_db
def test_profissional_service_cria_agregado(cargo_profissional):
    """Cria o profissional e sincroniza suas funções."""
    repository = MagicMock()
    repository.criar.return_value = profissional = {"id": 1}
    funcao_service = MagicMock()
    funcoes_criadas = [{"id": 2, "documentos": []}]
    funcao_service.sincronizar.return_value = funcoes_criadas
    service = ProfissionalService(repository, funcao_service)
    funcoes = [{"cargo": cargo_profissional}]

    resultado = service.criar(
        {
            "nome": "José",
            "cpf": "12345678901",
            "rg": "123456789",
            "funcoes": funcoes,
        }
    )

    repository.criar.assert_called_once_with(
        {
            "nome": "José",
            "cpf": "12345678901",
            "rg": "123456789",
            "criado_por": None,
        }
    )
    funcao_service.sincronizar.assert_called_once_with(1, funcoes, None)
    assert resultado == profissional
    assert resultado["funcoes"] == funcoes_criadas
