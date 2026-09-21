"""Testes do serviço de cargos."""

from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from apps.cargo.constants import CargoErrorMessages
from apps.cargo.exceptions import CargoOuDocumentoJaVinculadaError
from apps.cargo.models import Cargo
from apps.cargo.repository.cargo_repository import CargoRepository
from apps.cargo.services.cargo_service import CargoService
from apps.usuarios.models.usuario import Usuario


@pytest.fixture
def repository() -> MagicMock:
    """Retorna um repositório simulado.

    Returns:
        Repositório de cargos simulado.
    """
    repository_mock = MagicMock(spec=CargoRepository)
    repository_mock.existe_por_nome.return_value = False
    return repository_mock


@pytest.fixture
def service(
    repository: MagicMock,
) -> CargoService:
    """Retorna o serviço com o repositório simulado.

    Args:
        repository: Repositório utilizado pelo serviço.

    Returns:
        Serviço de cargos configurado para os testes.
    """
    return CargoService(
        repository=cast(CargoRepository, repository),
    )


@pytest.fixture
def usuario() -> MagicMock:
    """Retorna um usuário simulado.

    Returns:
        Usuário responsável pelo cadastro e atualização.
    """
    return MagicMock(spec=Usuario)


@pytest.fixture
def cargo() -> MagicMock:
    """Retorna um cargo simulado.

    Returns:
        Cargo utilizado nos testes de atualização.
    """
    cargo_mock = MagicMock(spec=Cargo)
    cargo_mock.pk = 1
    cargo_mock.nome = "Eletricista"
    cargo_mock.exige_documento = True
    cargo_mock.status = True
    return cargo_mock


@patch("apps.cargo.services.cargo_service.CargoRepository")
def test_inicializar_service_com_repository_padrao(
    cargo_repository_mock: MagicMock,
) -> None:
    """Deve utilizar o repositório padrão quando nenhum for informado."""
    repository_mock = MagicMock(spec=CargoRepository)
    cargo_repository_mock.return_value = repository_mock

    service = CargoService()

    cargo_repository_mock.assert_called_once_with()
    assert service.repository is repository_mock


def test_inicializar_service_com_repository_informado(
    repository: MagicMock,
) -> None:
    """Deve utilizar o repositório informado na inicialização."""
    service = CargoService(
        repository=cast(CargoRepository, repository),
    )

    assert service.repository is repository


def test_criar_cargo_normalizando_nome_e_documentos(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
) -> None:
    """Deve normalizar os nomes antes de criar o cargo."""
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

    repository.existe_por_nome.assert_called_once_with(
        "Eletricista",
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


def test_criar_deve_preservar_outros_campos_dos_documentos(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
) -> None:
    """Deve preservar os outros campos ao normalizar documentos."""
    repository.criar.return_value = {
        "pk": 1,
        "nome": "Eletricista",
    }

    service.criar(
        dados={
            "nome": "Eletricista",
            "exige_documento": True,
            "documentos": [
                {
                    "id": 10,
                    "nome": "  Certificado NR-10  ",
                },
            ],
        },
        usuario=usuario,
    )

    repository.criar.assert_called_once_with(
        {
            "nome": "Eletricista",
            "exige_documento": True,
            "documentos": [
                {
                    "id": 10,
                    "nome": "Certificado NR-10",
                },
            ],
        },
        usuario=usuario,
    )


def test_criar_nao_deve_alterar_dados_originais(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
) -> None:
    """Não deve alterar o dicionário original recebido pelo serviço."""
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
    repository.existe_por_nome.assert_called_once_with(
        "Eletricista",
    )


def test_criar_cargo_sem_documentos(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
) -> None:
    """Deve criar um cargo sem documentos quando não forem informados."""
    resultado_repository = {
        "pk": 1,
        "nome": "Auxiliar",
        "exige_documento": False,
        "status": True,
        "documentos": [],
    }
    repository.criar.return_value = resultado_repository

    resultado = service.criar(
        dados={
            "nome": "  Auxiliar  ",
            "exige_documento": False,
            "status": True,
        },
        usuario=usuario,
    )

    repository.existe_por_nome.assert_called_once_with(
        "Auxiliar",
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

    assert resultado == resultado_repository


def test_criar_deve_rejeitar_cargo_com_nome_duplicado(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
) -> None:
    """Deve rejeitar um cargo quando seu nome já estiver cadastrado."""
    repository.existe_por_nome.return_value = True

    with pytest.raises(
        CargoOuDocumentoJaVinculadaError,
    ) as exc_info:
        service.criar(
            dados={
                "nome": "  Eletricista  ",
                "exige_documento": False,
                "status": True,
            },
            usuario=usuario,
        )

    repository.existe_por_nome.assert_called_once_with(
        "Eletricista",
    )
    repository.criar.assert_not_called()

    assert exc_info.value.title == CargoErrorMessages.CARGO_VINCULADO_TITULO
    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.CARGO_VINCULADO_CORPO.format(
                nome="Eletricista",
            )
        ),
    }


def test_criar_deve_rejeitar_documentos_duplicados(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
) -> None:
    """Deve rejeitar documentos que possuam o mesmo nome."""
    with pytest.raises(
        CargoOuDocumentoJaVinculadaError,
    ) as exc_info:
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

    repository.existe_por_nome.assert_called_once_with(
        "Eletricista",
    )
    repository.criar.assert_not_called()

    assert (
        exc_info.value.title == CargoErrorMessages.DOCUMENTO_VINCULADO_TITULO
    )
    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.DOCUMENTO_VINCULADO_CORPO.format(
                nome_documento="Certificado NR-10",
                nome_cargo="Eletricista",
            )
        ),
    }


def test_criar_deve_rejeitar_documentos_duplicados_sem_diferenciar_caixa(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
) -> None:
    """Deve ignorar espaços e caixa ao verificar nomes duplicados."""
    with pytest.raises(
        CargoOuDocumentoJaVinculadaError,
    ) as exc_info:
        service.criar(
            dados={
                "nome": "  Eletricista  ",
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

    repository.existe_por_nome.assert_called_once_with(
        "Eletricista",
    )
    repository.criar.assert_not_called()

    assert (
        exc_info.value.title == CargoErrorMessages.DOCUMENTO_VINCULADO_TITULO
    )
    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.DOCUMENTO_VINCULADO_CORPO.format(
                nome_documento="CERTIFICADO NR-10",
                nome_cargo="Eletricista",
            )
        ),
    }


def test_criar_deve_permitir_documentos_com_nomes_diferentes(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
) -> None:
    """Deve permitir documentos que possuam nomes diferentes."""
    repository.criar.return_value = {
        "pk": 1,
        "nome": "Eletricista",
    }

    resultado = service.criar(
        dados={
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

    repository.existe_por_nome.assert_called_once_with(
        "Eletricista",
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

    assert resultado == repository.criar.return_value


def test_atualizar_cargo_normalizando_nome_e_documentos(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Deve normalizar os dados antes de atualizar o cargo."""
    dados = {
        "nome": "  Engenheiro Eletricista  ",
        "exige_documento": True,
        "status": False,
        "documentos": [
            {
                "nome": "  Certificado NR-10  ",
            },
            {
                "nome": "  Certificado NR-35  ",
            },
        ],
    }

    resultado_repository = {
        "pk": cargo.pk,
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
    repository.atualizar.return_value = resultado_repository

    resultado = service.atualizar(
        cargo=cargo,
        dados=dados,
        usuario=usuario,
    )

    repository.existe_por_nome.assert_called_once_with(
        "Engenheiro Eletricista",
        cargo_ignorado=cargo,
    )
    repository.atualizar.assert_called_once_with(
        cargo=cargo,
        dados={
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
        },
        usuario=usuario,
    )

    assert resultado == resultado_repository


def test_atualizar_deve_preservar_outros_campos_dos_documentos(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Deve preservar outros campos ao normalizar documentos."""
    service.atualizar(
        cargo=cargo,
        dados={
            "documentos": [
                {
                    "id": 10,
                    "nome": "  Certificado NR-10  ",
                },
            ],
        },
        usuario=usuario,
    )

    repository.existe_por_nome.assert_not_called()
    repository.atualizar.assert_called_once_with(
        cargo=cargo,
        dados={
            "documentos": [
                {
                    "id": 10,
                    "nome": "Certificado NR-10",
                },
            ],
        },
        usuario=usuario,
    )


def test_atualizar_apenas_campos_simples(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Deve atualizar campos simples sem validar nome ou documentos."""
    resultado_repository = {
        "pk": cargo.pk,
        "nome": cargo.nome,
        "exige_documento": cargo.exige_documento,
        "status": False,
    }
    repository.atualizar.return_value = resultado_repository

    resultado = service.atualizar(
        cargo=cargo,
        dados={
            "status": False,
        },
        usuario=usuario,
    )

    repository.existe_por_nome.assert_not_called()
    repository.atualizar.assert_called_once_with(
        cargo=cargo,
        dados={
            "status": False,
        },
        usuario=usuario,
    )

    assert resultado == resultado_repository


def test_atualizar_apenas_nome(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Deve normalizar e validar o nome recebido na atualização."""
    service.atualizar(
        cargo=cargo,
        dados={
            "nome": "  Engenheiro  ",
        },
        usuario=usuario,
    )

    repository.existe_por_nome.assert_called_once_with(
        "Engenheiro",
        cargo_ignorado=cargo,
    )
    repository.atualizar.assert_called_once_with(
        cargo=cargo,
        dados={
            "nome": "Engenheiro",
        },
        usuario=usuario,
    )


def test_atualizar_apenas_documentos_deve_usar_nome_atual_do_cargo(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Deve usar o nome atual do cargo ao validar seus documentos."""
    service.atualizar(
        cargo=cargo,
        dados={
            "documentos": [
                {
                    "nome": "  Certificado NR-10  ",
                },
                {
                    "nome": "  Certificado NR-35  ",
                },
            ],
        },
        usuario=usuario,
    )

    repository.existe_por_nome.assert_not_called()
    repository.atualizar.assert_called_once_with(
        cargo=cargo,
        dados={
            "documentos": [
                {
                    "nome": "Certificado NR-10",
                },
                {
                    "nome": "Certificado NR-35",
                },
            ],
        },
        usuario=usuario,
    )


def test_atualizar_com_lista_vazia_de_documentos(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Deve encaminhar lista vazia para remover documentos existentes."""
    service.atualizar(
        cargo=cargo,
        dados={
            "exige_documento": False,
            "documentos": [],
        },
        usuario=usuario,
    )

    repository.existe_por_nome.assert_not_called()
    repository.atualizar.assert_called_once_with(
        cargo=cargo,
        dados={
            "exige_documento": False,
            "documentos": [],
        },
        usuario=usuario,
    )


def test_atualizar_nao_deve_alterar_dados_originais(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Não deve alterar o dicionário original recebido na atualização."""
    dados = {
        "nome": "  Engenheiro Eletricista  ",
        "documentos": [
            {
                "nome": "  Certificado NR-10  ",
            },
        ],
    }
    dados_esperados = {
        "nome": "  Engenheiro Eletricista  ",
        "documentos": [
            {
                "nome": "  Certificado NR-10  ",
            },
        ],
    }

    service.atualizar(
        cargo=cargo,
        dados=dados,
        usuario=usuario,
    )

    assert dados == dados_esperados


def test_atualizar_deve_rejeitar_nome_utilizado_por_outro_cargo(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Deve rejeitar nome pertencente a outro cargo."""
    repository.existe_por_nome.return_value = True

    with pytest.raises(
        CargoOuDocumentoJaVinculadaError,
    ) as exc_info:
        service.atualizar(
            cargo=cargo,
            dados={
                "nome": "  Engenheiro Eletricista  ",
            },
            usuario=usuario,
        )

    repository.existe_por_nome.assert_called_once_with(
        "Engenheiro Eletricista",
        cargo_ignorado=cargo,
    )
    repository.atualizar.assert_not_called()

    assert exc_info.value.title == CargoErrorMessages.CARGO_VINCULADO_TITULO
    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.CARGO_VINCULADO_CORPO.format(
                nome="Engenheiro Eletricista",
            )
        ),
    }


def test_atualizar_deve_rejeitar_documentos_duplicados(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Deve rejeitar documentos duplicados durante a atualização."""
    with pytest.raises(
        CargoOuDocumentoJaVinculadaError,
    ) as exc_info:
        service.atualizar(
            cargo=cargo,
            dados={
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

    repository.existe_por_nome.assert_not_called()
    repository.atualizar.assert_not_called()

    assert (
        exc_info.value.title == CargoErrorMessages.DOCUMENTO_VINCULADO_TITULO
    )
    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.DOCUMENTO_VINCULADO_CORPO.format(
                nome_documento="CERTIFICADO NR-10",
                nome_cargo="Eletricista",
            )
        ),
    }


def test_atualizar_documentos_deve_usar_novo_nome_na_mensagem(
    service: CargoService,
    repository: MagicMock,
    usuario: MagicMock,
    cargo: MagicMock,
) -> None:
    """Deve usar o novo nome do cargo ao informar documento duplicado."""
    with pytest.raises(
        CargoOuDocumentoJaVinculadaError,
    ) as exc_info:
        service.atualizar(
            cargo=cargo,
            dados={
                "nome": "  Engenheiro Eletricista  ",
                "documentos": [
                    {
                        "nome": "Certificado NR-10",
                    },
                    {
                        "nome": "certificado nr-10",
                    },
                ],
            },
            usuario=usuario,
        )

    repository.existe_por_nome.assert_called_once_with(
        "Engenheiro Eletricista",
        cargo_ignorado=cargo,
    )
    repository.atualizar.assert_not_called()

    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.DOCUMENTO_VINCULADO_CORPO.format(
                nome_documento="certificado nr-10",
                nome_cargo="Engenheiro Eletricista",
            )
        ),
    }
