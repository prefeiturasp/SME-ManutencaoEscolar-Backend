"""Testes do serviço de cargos."""

from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.cargo.repository.cargo_repository import CargoRepository
from apps.cargo.services.cargo_service import CargoService
from apps.usuarios.models.usuario import Usuario


@patch("apps.cargo.services.cargo_service.CargoRepository")
def test_inicializar_service_com_repository_padrao(
    cargo_repository_mock: MagicMock,
) -> None:
    """Deve utilizar o repositório padrão quando nenhum for informado."""
    repository = MagicMock(spec=CargoRepository)
    cargo_repository_mock.return_value = repository

    service = CargoService()

    cargo_repository_mock.assert_called_once_with()
    assert service.repository == repository


def test_inicializar_service_com_repository_informado() -> None:
    """Deve utilizar o repositório informado na inicialização."""
    repository = MagicMock(spec=CargoRepository)

    service = CargoService(
        repository=cast(CargoRepository, repository),
    )

    assert service.repository == repository


def test_criar_cargo_normalizando_nome_e_documentos() -> None:
    """Deve normalizar os nomes antes de criar o cargo."""
    repository = MagicMock(spec=CargoRepository)
    service = CargoService(
        repository=cast(CargoRepository, repository),
    )
    usuario = MagicMock(spec=Usuario)

    dados = {
        "nome": "  Eletricista  ",
        "exige_documento": True,
        "status": True,
        "documentos": [
            {
                "nome": "  Certificado NR-10  ",
            },
            {
                "nome": "  Documento pessoal  ",
            },
        ],
    }

    resultado_repository = {
        "pk": 1,
        "nome": "Eletricista",
        "exige_documento": True,
        "status": True,
        "documentos": [
            {
                "nome": "Certificado NR-10",
            },
            {
                "nome": "Documento pessoal",
            },
        ],
    }
    repository.criar.return_value = resultado_repository

    resultado = service.criar(
        dados=dados,
        usuario=usuario,
    )

    repository.criar.assert_called_once_with(
        {
            "nome": "Eletricista",
            "exige_documento": True,
            "status": True,
            "documentos": [
                {
                    "nome": "Certificado NR-10",
                },
                {
                    "nome": "Documento pessoal",
                },
            ],
        },
        usuario=usuario,
    )
    assert resultado == resultado_repository


def test_nao_alterar_dados_originais_ao_criar_cargo() -> None:
    """Não deve alterar o dicionário original recebido pelo service."""
    repository = MagicMock(spec=CargoRepository)
    service = CargoService(
        repository=cast(CargoRepository, repository),
    )
    usuario = MagicMock(spec=Usuario)

    dados = {
        "nome": "  Eletricista  ",
        "exige_documento": True,
        "status": True,
        "documentos": [
            {
                "nome": "  Certificado NR-10  ",
            },
        ],
    }

    dados_esperados = {
        "nome": "  Eletricista  ",
        "exige_documento": True,
        "status": True,
        "documentos": [
            {
                "nome": "  Certificado NR-10  ",
            },
        ],
    }

    service.criar(
        dados=dados,
        usuario=usuario,
    )

    assert dados == dados_esperados


def test_criar_cargo_sem_documentos() -> None:
    """Deve criar um cargo sem documentos quando a lista não for enviada."""
    repository = MagicMock(spec=CargoRepository)
    service = CargoService(
        repository=cast(CargoRepository, repository),
    )
    usuario = MagicMock(spec=Usuario)

    repository.criar.return_value = {
        "pk": 1,
        "nome": "Auxiliar",
        "exige_documento": False,
        "status": True,
        "documentos": [],
    }

    resultado = service.criar(
        dados={
            "nome": "  Auxiliar  ",
            "exige_documento": False,
            "status": True,
        },
        usuario=usuario,
    )

    repository.criar.assert_called_once_with(
        {
            "nome": "Auxiliar",
            "exige_documento": False,
            "status": True,
            "documentos": [],
        },
        usuario=usuario,
    )
    assert resultado == repository.criar.return_value


def test_rejeitar_documentos_com_nomes_duplicados() -> None:
    """Deve rejeitar documentos que possuam o mesmo nome."""
    repository = MagicMock(spec=CargoRepository)
    service = CargoService(
        repository=cast(CargoRepository, repository),
    )
    usuario = MagicMock(spec=Usuario)

    with pytest.raises(ValidationError) as exc_info:
        service.criar(
            dados={
                "nome": "Eletricista",
                "exige_documento": True,
                "status": True,
                "documentos": [
                    {
                        "nome": "Certificado NR-10",
                    },
                    {
                        "nome": "Certificado NR-10",
                    },
                ],
            },
            usuario=usuario,
        )

    assert exc_info.value.message_dict == {
        "documentos": [
            "Não é permitido informar documentos com nomes duplicados.",
        ],
    }
    repository.criar.assert_not_called()


def test_rejeitar_documentos_duplicados_ignorando_espacos_e_caixa() -> None:
    """Deve ignorar espaços e caixa ao verificar nomes duplicados."""
    repository = MagicMock(spec=CargoRepository)
    service = CargoService(
        repository=cast(CargoRepository, repository),
    )
    usuario = MagicMock(spec=Usuario)

    with pytest.raises(ValidationError) as exc_info:
        service.criar(
            dados={
                "nome": "Eletricista",
                "exige_documento": True,
                "status": True,
                "documentos": [
                    {
                        "nome": "Certificado NR-10",
                    },
                    {
                        "nome": "  CERTIFICADO NR-10  ",
                    },
                ],
            },
            usuario=usuario,
        )

    assert exc_info.value.message_dict == {
        "documentos": [
            "Não é permitido informar documentos com nomes duplicados.",
        ],
    }
    repository.criar.assert_not_called()
