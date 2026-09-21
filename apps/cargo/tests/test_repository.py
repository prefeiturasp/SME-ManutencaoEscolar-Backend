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


@pytest.mark.parametrize(
    ("resultado_exists", "resultado_esperado"),
    [
        (True, True),
        (False, False),
    ],
)
def test_existe_por_nome(
    resultado_exists: bool,
    resultado_esperado: bool,
) -> None:
    """Deve informar se existe um cargo ativo com o nome recebido."""
    repository, cargo_model, _ = criar_mocks()
    queryset = MagicMock()

    cargo_model.objects.filter.return_value = queryset
    queryset.exists.return_value = resultado_exists

    resultado = repository.existe_por_nome("Eletricista")

    cargo_model.objects.filter.assert_called_once_with(
        nome__iexact="Eletricista",
        deletado_em__isnull=True,
    )
    queryset.exclude.assert_not_called()
    queryset.exists.assert_called_once_with()

    assert resultado is resultado_esperado


def test_existe_por_nome_deve_ignorar_cargo_informado() -> None:
    """Deve desconsiderar o cargo informado na busca por duplicidade."""
    repository, cargo_model, _ = criar_mocks()
    cargo_ignorado = MagicMock(spec=Cargo)
    cargo_ignorado.pk = 10

    queryset_filtrado = MagicMock()
    queryset_excluido = MagicMock()

    cargo_model.objects.filter.return_value = queryset_filtrado
    queryset_filtrado.exclude.return_value = queryset_excluido
    queryset_excluido.exists.return_value = False

    resultado = repository.existe_por_nome(
        "Eletricista",
        cargo_ignorado=cargo_ignorado,
    )

    cargo_model.objects.filter.assert_called_once_with(
        nome__iexact="Eletricista",
        deletado_em__isnull=True,
    )
    queryset_filtrado.exclude.assert_called_once_with(
        pk=cargo_ignorado.pk,
    )
    queryset_excluido.exists.assert_called_once_with()

    assert resultado is False


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
        ],
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
    """Deve criar um cargo sem documentos."""
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

    dados = {
        "nome": "Auxiliar",
        "exige_documento": False,
        "status": True,
    }

    resultado = repository.criar(
        dados=dados,
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
def test_criar_nao_deve_alterar_dados_originais(
    model_to_dict_mock: MagicMock,
) -> None:
    """Não deve alterar o dicionário original recebido na criação."""
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


def test_criar_nao_deve_salvar_cargo_invalido() -> None:
    """Não deve salvar o cargo quando sua validação falhar."""
    repository, cargo_model, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.full_clean.side_effect = ValidationError(
        {
            "nome": [
                "Nome inválido.",
            ],
        },
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


def test_criar_nao_deve_persistir_documento_invalido() -> None:
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
        },
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


@patch("apps.cargo.repository.cargo_repository.model_to_dict")
def test_atualizar_cargo_e_substituir_documentos(
    model_to_dict_mock: MagicMock,
) -> None:
    """Deve atualizar o cargo e substituir seus documentos."""
    repository, _, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.pk = 4
    cargo.uuid = uuid4()
    cargo.nome = "Eletricista"
    cargo.exige_documento = True
    cargo.status = True

    queryset_documentos = MagicMock()
    documento_model.objects.filter.return_value = queryset_documentos

    primeiro_documento = MagicMock(spec=DocumentoCargo)
    segundo_documento = MagicMock(spec=DocumentoCargo)

    documento_model.side_effect = [
        primeiro_documento,
        segundo_documento,
    ]

    model_to_dict_mock.return_value = {
        "nome": "Engenheiro Eletricista",
        "exige_documento": True,
        "status": False,
    }

    dados = {
        "nome": "Engenheiro Eletricista",
        "exige_documento": True,
        "status": False,
        "documentos": [
            {
                "nome": "Certificado NR-10",
            },
            {
                "nome": "Certificado NR-35",
            },
        ],
    }

    resultado = repository.atualizar(
        cargo=cargo,
        dados=dados,
        usuario=usuario,
    )

    assert cargo.nome == "Engenheiro Eletricista"
    assert cargo.exige_documento is True
    assert cargo.status is False
    assert cargo.atualizado_por is usuario

    cargo.full_clean.assert_called_once_with()
    cargo.save.assert_called_once_with()

    documento_model.objects.filter.assert_called_once_with(
        cargo=cargo,
    )
    queryset_documentos.delete.assert_called_once_with()

    assert documento_model.call_args_list == [
        call(
            nome="Certificado NR-10",
            cargo=cargo,
            criado_por=usuario,
            atualizado_por=usuario,
        ),
        call(
            nome="Certificado NR-35",
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
        ],
    )

    model_to_dict_mock.assert_called_once_with(cargo)

    assert resultado == {
        "nome": "Engenheiro Eletricista",
        "exige_documento": True,
        "status": False,
        "documentos": [
            primeiro_documento,
            segundo_documento,
        ],
        "uuid": cargo.uuid,
        "pk": cargo.pk,
    }


@patch("apps.cargo.repository.cargo_repository.model_to_dict")
def test_atualizar_cargo_sem_alterar_documentos(
    model_to_dict_mock: MagicMock,
) -> None:
    """Deve manter os documentos quando o campo não for informado."""
    repository, _, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.pk = 5
    cargo.uuid = uuid4()
    cargo.nome = "Eletricista"
    cargo.status = True

    documento_existente = MagicMock(spec=DocumentoCargo)
    queryset_documentos = MagicMock()
    queryset_documentos.__iter__.return_value = iter(
        [documento_existente],
    )
    documento_model.objects.filter.return_value = queryset_documentos

    model_to_dict_mock.return_value = {
        "nome": "Eletricista atualizado",
        "status": True,
    }

    resultado = repository.atualizar(
        cargo=cargo,
        dados={
            "nome": "Eletricista atualizado",
        },
        usuario=usuario,
    )

    assert cargo.nome == "Eletricista atualizado"
    assert cargo.atualizado_por is usuario

    cargo.full_clean.assert_called_once_with()
    cargo.save.assert_called_once_with()

    documento_model.objects.filter.assert_called_once_with(
        cargo=cargo,
    )
    queryset_documentos.delete.assert_not_called()

    documento_model.assert_not_called()
    documento_model.objects.bulk_create.assert_not_called()

    model_to_dict_mock.assert_called_once_with(cargo)

    assert resultado == {
        "nome": "Eletricista atualizado",
        "status": True,
        "documentos": [
            documento_existente,
        ],
        "uuid": cargo.uuid,
        "pk": cargo.pk,
    }


@patch("apps.cargo.repository.cargo_repository.model_to_dict")
def test_atualizar_com_lista_vazia_deve_remover_documentos(
    model_to_dict_mock: MagicMock,
) -> None:
    """Deve remover documentos quando uma lista vazia for informada."""
    repository, _, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.pk = 6
    cargo.uuid = uuid4()
    cargo.exige_documento = True

    queryset_documentos = MagicMock()
    documento_model.objects.filter.return_value = queryset_documentos

    model_to_dict_mock.return_value = {
        "nome": "Auxiliar",
        "exige_documento": False,
        "status": True,
    }

    resultado = repository.atualizar(
        cargo=cargo,
        dados={
            "exige_documento": False,
            "documentos": [],
        },
        usuario=usuario,
    )

    assert cargo.exige_documento is False
    assert cargo.atualizado_por is usuario

    cargo.full_clean.assert_called_once_with()
    cargo.save.assert_called_once_with()

    documento_model.objects.filter.assert_called_once_with(
        cargo=cargo,
    )
    queryset_documentos.delete.assert_called_once_with()

    documento_model.assert_not_called()
    documento_model.objects.bulk_create.assert_called_once_with([])

    assert resultado == {
        "nome": "Auxiliar",
        "exige_documento": False,
        "status": True,
        "documentos": [],
        "uuid": cargo.uuid,
        "pk": cargo.pk,
    }


@patch("apps.cargo.repository.cargo_repository.model_to_dict")
def test_atualizar_nao_deve_alterar_dados_originais(
    model_to_dict_mock: MagicMock,
) -> None:
    """Não deve modificar o dicionário recebido na atualização."""
    repository, _, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.pk = 7
    cargo.uuid = uuid4()

    queryset_documentos = MagicMock()
    documento_model.objects.filter.return_value = queryset_documentos

    documento = MagicMock(spec=DocumentoCargo)
    documento_model.return_value = documento

    model_to_dict_mock.return_value = {
        "nome": "Eletricista atualizado",
        "exige_documento": True,
    }

    dados = {
        "nome": "Eletricista atualizado",
        "exige_documento": True,
        "documentos": [
            {
                "nome": "Certificado NR-10",
            },
        ],
    }

    dados_esperados = {
        "nome": "Eletricista atualizado",
        "exige_documento": True,
        "documentos": [
            {
                "nome": "Certificado NR-10",
            },
        ],
    }

    repository.atualizar(
        cargo=cargo,
        dados=dados,
        usuario=usuario,
    )

    assert dados == dados_esperados


def test_atualizar_nao_deve_salvar_cargo_invalido() -> None:
    """Não deve salvar o cargo quando sua validação falhar."""
    repository, _, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.nome = "Eletricista"
    cargo.full_clean.side_effect = ValidationError(
        {
            "nome": [
                "Nome inválido.",
            ],
        },
    )

    with pytest.raises(ValidationError) as exc_info:
        repository.atualizar(
            cargo=cargo,
            dados={
                "nome": "",
                "documentos": [],
            },
            usuario=usuario,
        )

    assert exc_info.value.message_dict == {
        "nome": [
            "Nome inválido.",
        ],
    }

    assert cargo.nome == ""
    assert cargo.atualizado_por is usuario

    cargo.full_clean.assert_called_once_with()
    cargo.save.assert_not_called()

    documento_model.objects.filter.assert_not_called()
    documento_model.objects.bulk_create.assert_not_called()


def test_atualizar_nao_deve_persistir_documento_invalido() -> None:
    """Não deve persistir documentos novos quando a validação falhar."""
    repository, _, documento_model = criar_mocks()
    usuario = MagicMock(spec=Usuario)

    cargo = MagicMock(spec=Cargo)
    cargo.pk = 8
    cargo.uuid = uuid4()

    queryset_documentos = MagicMock()
    documento_model.objects.filter.return_value = queryset_documentos

    documento = MagicMock(spec=DocumentoCargo)
    documento.full_clean.side_effect = ValidationError(
        {
            "nome": [
                "Nome inválido.",
            ],
        },
    )
    documento_model.return_value = documento

    with pytest.raises(ValidationError) as exc_info:
        repository.atualizar(
            cargo=cargo,
            dados={
                "nome": "Eletricista",
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

    documento_model.objects.filter.assert_called_once_with(
        cargo=cargo,
    )
    queryset_documentos.delete.assert_called_once_with()

    documento.full_clean.assert_called_once_with()
    documento_model.objects.bulk_create.assert_not_called()
