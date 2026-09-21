"""Testes do serviço de cargos."""

from copy import deepcopy

import pytest

from apps.cargo.constants import CargoErrorMessages
from apps.cargo.exceptions import CargoOuDocumentoJaVinculadaError
from apps.cargo.models import Cargo, DocumentoCargo
from apps.cargo.repository.cargo_repository import CargoRepository
from apps.cargo.services.cargo_service import CargoService

pytestmark = pytest.mark.django_db


def test_inicializar_service_com_repository_padrao():
    """Deve utilizar o repositório padrão quando não for informado."""
    service = CargoService()

    assert isinstance(service.repository, CargoRepository)


def test_inicializar_service_com_repository_informado():
    """Deve utilizar o repositório informado na inicialização."""
    repository = CargoRepository()

    service = CargoService(repository=repository)

    assert service.repository is repository


def test_criar_cargo_normalizando_nome_e_documentos(
    cargo_payload_valido,
    service,
    usuario_ativo,
):
    """Deve normalizar os nomes antes de criar o cargo."""
    resultado = service.criar(
        dados={
            **cargo_payload_valido,
            "nome": "  Engenheiro Eletricista  ",
            "documentos": [
                {"nome": f"  {documento['nome']}  "}
                for documento in cargo_payload_valido["documentos"]
            ],
        },
        usuario=usuario_ativo,
    )

    cargo_criado = Cargo.objects.get(
        pk=resultado["pk"],
    )
    documentos = list(
        DocumentoCargo.objects.filter(
            cargo=cargo_criado,
        ).order_by("nome")
    )

    assert cargo_criado.nome == "Engenheiro Eletricista"
    assert cargo_criado.exige_documento is True
    assert cargo_criado.status is True
    assert cargo_criado.criado_por == usuario_ativo
    assert cargo_criado.atualizado_por == usuario_ativo

    assert len(documentos) == 2
    assert documentos[0].nome == "Certificado NR-10"
    assert documentos[1].nome == "Certificado NR-35"

    assert resultado["pk"] == cargo_criado.pk
    assert resultado["uuid"] == cargo_criado.uuid


def test_criar_cargo_sem_documentos(
    cargo_payload_valido_sem_documentos,
    service,
    usuario_ativo,
):
    """Deve criar um cargo sem documentos."""
    resultado = service.criar(
        dados={
            **cargo_payload_valido_sem_documentos,
            "nome": "  Auxiliar Administrativo  ",
        },
        usuario=usuario_ativo,
    )

    cargo_criado = Cargo.objects.get(
        pk=resultado["pk"],
    )

    assert cargo_criado.nome == "Auxiliar Administrativo"
    assert cargo_criado.exige_documento is False
    assert cargo_criado.status is True
    assert cargo_criado.criado_por == usuario_ativo
    assert cargo_criado.atualizado_por == usuario_ativo

    assert not DocumentoCargo.objects.filter(
        cargo=cargo_criado,
    ).exists()

    assert resultado["documentos"] == []


def test_criar_nao_deve_alterar_dados_originais(
    cargo_payload_valido,
    service,
    usuario_ativo,
):
    """Não deve alterar os dados originais recebidos na criação."""
    dados = {
        **cargo_payload_valido,
        "nome": "  Engenheiro Eletricista  ",
        "documentos": [
            {"nome": "  Certificado NR-10  "},
        ],
    }
    dados_esperados = deepcopy(dados)

    service.criar(
        dados=dados,
        usuario=usuario_ativo,
    )

    assert dados == dados_esperados


def test_criar_deve_rejeitar_cargo_com_nome_duplicado(
    cargo,
    cargo_payload_valido_sem_documentos,
    service,
    usuario_ativo,
):
    """Deve rejeitar um cargo quando seu nome já estiver cadastrado."""
    with pytest.raises(
        CargoOuDocumentoJaVinculadaError,
    ) as exc_info:
        service.criar(
            dados={
                **cargo_payload_valido_sem_documentos,
                "nome": "  Eletricista  ",
            },
            usuario=usuario_ativo,
        )

    assert exc_info.value.title == CargoErrorMessages.CARGO_VINCULADO_TITULO
    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.CARGO_VINCULADO_CORPO.format(
                nome="Eletricista",
            )
        ),
    }

    assert (
        Cargo.objects.filter(
            nome__iexact="Eletricista",
        ).count()
        == 1
    )

    assert (
        Cargo.objects.get(
            nome__iexact="Eletricista",
        ).pk
        == cargo.pk
    )


@pytest.mark.parametrize(
    ("primeiro_nome", "segundo_nome", "nome_erro"),
    [
        (
            "Certificado NR-10",
            "Certificado NR-10",
            "Certificado NR-10",
        ),
        (
            "Certificado NR-10",
            "  CERTIFICADO NR-10  ",
            "CERTIFICADO NR-10",
        ),
    ],
)
def test_criar_deve_rejeitar_documentos_duplicados(
    cargo_payload_valido,
    service,
    usuario_ativo,
    primeiro_nome,
    segundo_nome,
    nome_erro,
):
    """Deve rejeitar documentos com nomes duplicados."""
    nome_cargo = "Cargo com documentos duplicados"

    with pytest.raises(
        CargoOuDocumentoJaVinculadaError,
    ) as exc_info:
        service.criar(
            dados={
                **cargo_payload_valido,
                "nome": nome_cargo,
                "documentos": [
                    {
                        "nome": primeiro_nome,
                    },
                    {
                        "nome": segundo_nome,
                    },
                ],
            },
            usuario=usuario_ativo,
        )

    assert (
        exc_info.value.title == CargoErrorMessages.DOCUMENTO_VINCULADO_TITULO
    )
    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.DOCUMENTO_VINCULADO_CORPO.format(
                nome_documento=nome_erro,
                nome_cargo=nome_cargo,
            )
        ),
    }

    assert not Cargo.objects.filter(
        nome=nome_cargo,
    ).exists()


def test_criar_deve_permitir_documentos_com_nomes_diferentes(
    cargo_payload_valido,
    service,
    usuario_ativo,
):
    """Deve permitir documentos com nomes diferentes."""
    resultado = service.criar(
        dados={
            **cargo_payload_valido,
            "nome": "Técnico Eletricista",
        },
        usuario=usuario_ativo,
    )

    cargo_criado = Cargo.objects.get(
        pk=resultado["pk"],
    )
    nomes_documentos = set(
        DocumentoCargo.objects.filter(
            cargo=cargo_criado,
        ).values_list(
            "nome",
            flat=True,
        )
    )

    assert nomes_documentos == {
        "Certificado NR-10",
        "Certificado NR-35",
    }


def test_atualizar_cargo_normalizando_nome_e_documentos(
    cargo,
    cargo_payload_valido,
    documento_cargo,
    service,
    usuario_ativo,
):
    """Deve normalizar nome e documentos antes da atualização."""
    resultado = service.atualizar(
        cargo=cargo,
        dados={
            **cargo_payload_valido,
            "nome": "  Engenheiro Eletricista  ",
            "status": False,
            "documentos": [
                {"nome": f"  {documento['nome']}  "}
                for documento in cargo_payload_valido["documentos"]
            ],
        },
        usuario=usuario_ativo,
    )

    cargo.refresh_from_db()

    nomes_documentos = set(
        DocumentoCargo.objects.filter(
            cargo=cargo,
        ).values_list(
            "nome",
            flat=True,
        )
    )

    assert cargo.nome == "Engenheiro Eletricista"
    assert cargo.exige_documento is True
    assert cargo.status is False
    assert cargo.atualizado_por == usuario_ativo

    assert nomes_documentos == {
        "Certificado NR-10",
        "Certificado NR-35",
    }

    assert not DocumentoCargo.objects.filter(
        pk=documento_cargo.pk,
    ).exists()

    assert resultado["pk"] == cargo.pk
    assert resultado["uuid"] == cargo.uuid


def test_atualizar_apenas_campos_simples(
    cargo,
    documento_cargo,
    service,
    usuario_ativo,
):
    """Deve atualizar campos simples sem substituir documentos."""
    service.atualizar(
        cargo=cargo,
        dados={
            "status": False,
        },
        usuario=usuario_ativo,
    )

    cargo.refresh_from_db()
    documento_cargo.refresh_from_db()

    assert cargo.status is False
    assert cargo.nome == "Eletricista"
    assert cargo.atualizado_por == usuario_ativo

    assert DocumentoCargo.objects.filter(
        pk=documento_cargo.pk,
        cargo=cargo,
    ).exists()


def test_atualizar_apenas_nome(
    cargo,
    service,
    usuario_ativo,
):
    """Deve normalizar e atualizar somente o nome."""
    service.atualizar(
        cargo=cargo,
        dados={
            "nome": "  Engenheiro  ",
        },
        usuario=usuario_ativo,
    )

    cargo.refresh_from_db()

    assert cargo.nome == "Engenheiro"
    assert cargo.exige_documento is False
    assert cargo.status is True
    assert cargo.atualizado_por == usuario_ativo


def test_atualizar_apenas_documentos(
    cargo,
    documentos_cargo_payload_valido,
    service,
    usuario_ativo,
):
    """Deve normalizar documentos usando o nome atual do cargo."""
    service.atualizar(
        cargo=cargo,
        dados={
            "documentos": [
                {"nome": f"  {documento['nome']}  "}
                for documento in documentos_cargo_payload_valido
            ],
        },
        usuario=usuario_ativo,
    )

    cargo.refresh_from_db()

    nomes_documentos = set(
        DocumentoCargo.objects.filter(
            cargo=cargo,
        ).values_list(
            "nome",
            flat=True,
        )
    )

    assert cargo.nome == "Eletricista"
    assert nomes_documentos == {
        "Certificado NR-10",
        "Certificado NR-35",
    }


def test_atualizar_com_lista_vazia_de_documentos(
    cargo,
    documento_cargo,
    service,
    usuario_ativo,
):
    """Deve remover os documentos quando recebe uma lista vazia."""
    service.atualizar(
        cargo=cargo,
        dados={
            "exige_documento": False,
            "documentos": [],
        },
        usuario=usuario_ativo,
    )

    cargo.refresh_from_db()

    assert cargo.exige_documento is False
    assert not DocumentoCargo.objects.filter(
        cargo=cargo,
    ).exists()


def test_atualizar_nao_deve_alterar_dados_originais(
    cargo,
    cargo_payload_atualizacao_valido,
    service,
    usuario_ativo,
):
    """Não deve modificar os dados originais da atualização."""
    dados = {
        **cargo_payload_atualizacao_valido,
        "nome": "  Eletricista atualizado  ",
        "documentos": [
            {
                "nome": "  Certificado NR-10  ",
            },
        ],
    }
    dados_esperados = deepcopy(dados)

    service.atualizar(
        cargo=cargo,
        dados=dados,
        usuario=usuario_ativo,
    )

    assert dados == dados_esperados


def test_atualizar_deve_permitir_manter_o_proprio_nome(
    cargo,
    service,
    usuario_ativo,
):
    """Deve ignorar o próprio cargo na validação do nome."""
    service.atualizar(
        cargo=cargo,
        dados={
            "nome": "  Eletricista  ",
        },
        usuario=usuario_ativo,
    )

    cargo.refresh_from_db()

    assert cargo.nome == "Eletricista"


def test_atualizar_deve_rejeitar_nome_de_outro_cargo(
    cargo,
    service,
    usuario_ativo,
):
    """Deve rejeitar nome utilizado por outro cargo."""
    outro_cargo = Cargo.objects.create(
        nome="Encanador",
        exige_documento=False,
        status=True,
    )

    with pytest.raises(
        CargoOuDocumentoJaVinculadaError,
    ) as exc_info:
        service.atualizar(
            cargo=cargo,
            dados={
                "nome": "  Encanador  ",
            },
            usuario=usuario_ativo,
        )

    assert exc_info.value.title == CargoErrorMessages.CARGO_VINCULADO_TITULO
    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.CARGO_VINCULADO_CORPO.format(
                nome="Encanador",
            )
        ),
    }

    cargo.refresh_from_db()
    outro_cargo.refresh_from_db()

    assert cargo.nome == "Eletricista"
    assert outro_cargo.nome == "Encanador"


def test_atualizar_deve_rejeitar_documentos_duplicados(
    cargo,
    service,
    usuario_ativo,
):
    """Deve rejeitar documentos duplicados na atualização."""
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
            usuario=usuario_ativo,
        )

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

    assert not DocumentoCargo.objects.filter(
        cargo=cargo,
    ).exists()


def test_atualizar_documentos_deve_usar_novo_nome_na_mensagem(
    cargo,
    service,
    usuario_ativo,
):
    """Deve usar o novo nome ao informar documentos duplicados."""
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
            usuario=usuario_ativo,
        )

    assert exc_info.value.detail == {
        "message": (
            CargoErrorMessages.DOCUMENTO_VINCULADO_CORPO.format(
                nome_documento="certificado nr-10",
                nome_cargo="Engenheiro Eletricista",
            )
        ),
    }

    cargo.refresh_from_db()

    assert cargo.nome == "Eletricista"
