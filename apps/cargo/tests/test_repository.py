"""Testes do repositório de cargos."""

from typing import cast
from unittest.mock import MagicMock, call, patch
from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError

from apps.cargo.models import Cargo, DocumentoCargo
from apps.cargo.repository.cargo_repository import CargoRepository
from apps.usuarios.models.usuario import Usuario

MocksRepository = tuple[
    CargoRepository,
    MagicMock,
    MagicMock,
]

pytestmark = pytest.mark.django_db


def criar_mocks() -> MocksRepository:
    """Cria o repositório com os models simulados.

    Returns:
        Tupla contendo o repositório e os mocks dos models.
    """
    repository = CargoRepository()
    cargo_model = MagicMock()
    documento_model = MagicMock()

    repository.model = cast(type[Cargo], cargo_model)
    repository.documento_model = cast(
        type[DocumentoCargo],
        documento_model,
    )

    return repository, cargo_model, documento_model


@patch("apps.cargo.repository.cargo_repository.model_to_dict")
def test_criar_cargo_com_documentos(
    model_to_dict_mock: MagicMock,
) -> None:
    """Deve criar um cargo e seus documentos."""
    repository, cargo_model, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.pk = 1
    cargo.uuid = uuid4()
    cargo_model.return_value = cargo

    primeiro_documento = MagicMock(spec=DocumentoCargo)
    segundo_documento = MagicMock(spec=DocumentoCargo)

    documento_model.side_effect = [
        primeiro_documento,
        segundo_documento,
    ]

    model_to_dict_mock.return_value = {
        "nome": "Eletricista",
        "exige_documento": True,
        "status": True,
    }

    dados = {
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

    resultado = repository.criar(
        dados=dados,
        usuario=usuario,
    )

    cargo_model.assert_called_once_with(
        nome="Eletricista",
        exige_documento=True,
        status=True,
        criado_por=usuario,
        atualizado_por=usuario,
    )
    cargo.full_clean.assert_called_once_with()
    cargo.save.assert_called_once_with()

    assert documento_model.call_args_list == [
        call(
            nome="Certificado NR-10",
            cargo=cargo,
            criado_por=usuario,
            atualizado_por=usuario,
        ),
        call(
            nome="Documento pessoal",
            cargo=cargo,
            criado_por=usuario,
            atualizado_por=usuario,
        ),
    ]

    primeiro_documento.full_clean.assert_called_once_with()
    segundo_documento.full_clean.assert_called_once_with()

    documento_model.objects.bulk_create.assert_called_once_with(
        [
            primeiro_documento,
            segundo_documento,
        ]
    )
    model_to_dict_mock.assert_called_once_with(cargo)

    assert resultado == {
        "nome": "Eletricista",
        "exige_documento": True,
        "status": True,
        "documentos": [
            primeiro_documento,
            segundo_documento,
        ],
        "uuid": cargo.uuid,
        "pk": cargo.pk,
    }


@patch("apps.cargo.repository.cargo_repository.model_to_dict")
def test_criar_cargo_sem_documentos(
    model_to_dict_mock: MagicMock,
) -> None:
    """Deve criar um cargo quando documentos não forem informados."""
    repository, cargo_model, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.pk = 2
    cargo.uuid = uuid4()
    cargo_model.return_value = cargo

    model_to_dict_mock.return_value = {
        "nome": "Auxiliar",
        "exige_documento": False,
        "status": True,
    }

    resultado = repository.criar(
        dados={
            "nome": "Auxiliar",
            "exige_documento": False,
            "status": True,
        },
        usuario=usuario,
    )

    cargo_model.assert_called_once_with(
        nome="Auxiliar",
        exige_documento=False,
        status=True,
        criado_por=usuario,
        atualizado_por=usuario,
    )
    cargo.full_clean.assert_called_once_with()
    cargo.save.assert_called_once_with()

    documento_model.assert_not_called()
    documento_model.objects.bulk_create.assert_called_once_with([])
    model_to_dict_mock.assert_called_once_with(cargo)

    assert resultado == {
        "nome": "Auxiliar",
        "exige_documento": False,
        "status": True,
        "documentos": [],
        "uuid": cargo.uuid,
        "pk": cargo.pk,
    }


@patch("apps.cargo.repository.cargo_repository.model_to_dict")
def test_nao_alterar_dados_originais(
    model_to_dict_mock: MagicMock,
) -> None:
    """Não deve alterar o dicionário original recebido."""
    repository, cargo_model, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.pk = 3
    cargo.uuid = uuid4()
    cargo_model.return_value = cargo

    documento = MagicMock(spec=DocumentoCargo)
    documento_model.return_value = documento

    model_to_dict_mock.return_value = {
        "nome": "Eletricista",
        "exige_documento": True,
        "status": True,
    }

    dados = {
        "nome": "Eletricista",
        "exige_documento": True,
        "status": True,
        "documentos": [
            {
                "nome": "Certificado NR-10",
            },
        ],
    }
    dados_esperados = {
        "nome": "Eletricista",
        "exige_documento": True,
        "status": True,
        "documentos": [
            {
                "nome": "Certificado NR-10",
            },
        ],
    }

    repository.criar(
        dados=dados,
        usuario=usuario,
    )

    assert dados == dados_esperados


def test_nao_salvar_cargo_quando_validacao_falhar() -> None:
    """Não deve salvar o cargo quando sua validação falhar."""
    repository, cargo_model, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.full_clean.side_effect = ValidationError(
        {
            "nome": [
                "Nome inválido.",
            ],
        }
    )
    cargo_model.return_value = cargo

    with pytest.raises(ValidationError) as exc_info:
        repository.criar(
            dados={
                "nome": "",
                "exige_documento": False,
                "status": True,
            },
            usuario=usuario,
        )

    assert exc_info.value.message_dict == {
        "nome": [
            "Nome inválido.",
        ],
    }
    cargo.full_clean.assert_called_once_with()
    cargo.save.assert_not_called()
    documento_model.assert_not_called()
    documento_model.objects.bulk_create.assert_not_called()


def test_nao_criar_documentos_quando_validacao_falhar() -> None:
    """Não deve persistir documentos quando sua validação falhar."""
    repository, cargo_model, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo_model.return_value = cargo

    documento = MagicMock(spec=DocumentoCargo)
    documento.full_clean.side_effect = ValidationError(
        {
            "nome": [
                "Nome inválido.",
            ],
        }
    )
    documento_model.return_value = documento

    with pytest.raises(ValidationError) as exc_info:
        repository.criar(
            dados={
                "nome": "Eletricista",
                "exige_documento": True,
                "status": True,
                "documentos": [
                    {
                        "nome": "",
                    },
                ],
            },
            usuario=usuario,
        )

    assert exc_info.value.message_dict == {
        "nome": [
            "Nome inválido.",
        ],
    }
    cargo.full_clean.assert_called_once_with()
    cargo.save.assert_called_once_with()
    documento.full_clean.assert_called_once_with()
    documento_model.objects.bulk_create.assert_not_called()
