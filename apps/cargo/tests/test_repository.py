"""Testes do repositório de cargos."""

from copy import deepcopy

import pytest
from django.core.exceptions import ValidationError

from apps.cargo.models import Cargo, DocumentoCargo
from apps.cargo.repository.cargo_repository import CargoRepository

pytestmark = pytest.mark.django_db


def test_existe_por_nome_deve_retornar_true(
    cargo,
):
    """Deve encontrar um cargo ativo pelo nome."""
    repository = CargoRepository()

    resultado = repository.existe_por_nome("Eletricista")

    assert resultado is True


def test_existe_por_nome_deve_ignorar_diferenca_de_caixa(
    cargo,
):
    """Deve consultar o nome sem diferenciar maiúsculas e minúsculas."""
    repository = CargoRepository()

    resultado = repository.existe_por_nome("eLeTrIcIsTa")

    assert resultado is True


def test_existe_por_nome_deve_retornar_false(
    cargo,
):
    """Deve retornar False quando o cargo não existe."""
    repository = CargoRepository()

    resultado = repository.existe_por_nome("Encanador")

    assert resultado is False


def test_existe_por_nome_deve_ignorar_cargo_informado(
    cargo,
):
    """Deve desconsiderar o próprio cargo na busca por duplicidade."""
    repository = CargoRepository()

    resultado = repository.existe_por_nome(
        "Eletricista",
        cargo_ignorado=cargo,
    )

    assert resultado is False


def test_existe_por_nome_deve_encontrar_outro_cargo(
    cargo,
):
    """Deve encontrar um cargo diferente daquele ignorado."""
    Cargo.objects.create(
        nome="Encanador",
        exige_documento=False,
        status=True,
    )
    repository = CargoRepository()

    resultado = repository.existe_por_nome(
        "Encanador",
        cargo_ignorado=cargo,
    )

    assert resultado is True


def test_existe_por_nome_deve_ignorar_cargo_deletado(
    cargo_deletado,
):
    """Deve ignorar cargos deletados logicamente."""
    repository = CargoRepository()

    resultado = repository.existe_por_nome(
        cargo_deletado.nome,
    )

    assert resultado is False


def test_criar_cargo_com_documentos(
    cargo_payload_valido,
    usuario_ativo,
):
    """Deve criar um cargo e seus documentos."""
    repository = CargoRepository()

    resultado = repository.criar(
        dados=cargo_payload_valido,
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

    assert documentos[0].criado_por == usuario_ativo
    assert documentos[0].atualizado_por == usuario_ativo
    assert documentos[1].criado_por == usuario_ativo
    assert documentos[1].atualizado_por == usuario_ativo

    assert resultado["pk"] == cargo_criado.pk
    assert resultado["uuid"] == cargo_criado.uuid
    assert [documento.uuid for documento in resultado["documentos"]] == [
        documento.uuid for documento in documentos
    ]


def test_criar_cargo_sem_documentos(
    cargo_payload_valido_sem_documentos,
    usuario_ativo,
):
    """Deve criar um cargo sem documentos."""
    repository = CargoRepository()

    resultado = repository.criar(
        dados=cargo_payload_valido_sem_documentos,
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
    assert resultado["uuid"] == cargo_criado.uuid
    assert resultado["pk"] == cargo_criado.pk


def test_criar_nao_deve_alterar_dados_originais(
    cargo_payload_valido,
    usuario_ativo,
):
    """Não deve modificar os dados recebidos na criação."""
    repository = CargoRepository()

    dados = cargo_payload_valido
    dados_esperados = deepcopy(cargo_payload_valido)

    repository.criar(
        dados=dados,
        usuario=usuario_ativo,
    )

    assert dados == dados_esperados


def test_criar_nao_deve_persistir_cargo_invalido(
    cargo_payload_valido_sem_documentos,
    usuario_ativo,
):
    """Não deve persistir o cargo quando sua validação falhar."""
    repository = CargoRepository()

    with pytest.raises(ValidationError):
        repository.criar(
            dados={
                **cargo_payload_valido_sem_documentos,
                "nome": "",
            },
            usuario=usuario_ativo,
        )

    assert not Cargo.objects.filter(
        nome="",
    ).exists()


def test_criar_deve_desfazer_transacao_com_documento_invalido(
    cargo_payload_valido,
    usuario_ativo,
):
    """Deve desfazer a criação quando um documento for inválido."""
    repository = CargoRepository()
    nome_cargo = "Cargo com documento inválido"

    with pytest.raises(ValidationError):
        repository.criar(
            dados={
                **cargo_payload_valido,
                "nome": nome_cargo,
                "documentos": [
                    {
                        "nome": "",
                    },
                ],
            },
            usuario=usuario_ativo,
        )

    assert not Cargo.objects.filter(
        nome=nome_cargo,
    ).exists()

    assert not DocumentoCargo.objects.filter(
        nome="",
    ).exists()


def test_atualizar_cargo_e_substituir_documentos(
    cargo,
    cargo_payload_atualizacao_valido,
    documento_cargo,
    usuario_ativo,
):
    """Deve atualizar o cargo e substituir seus documentos."""
    repository = CargoRepository()

    resultado = repository.atualizar(
        cargo=cargo,
        dados=cargo_payload_atualizacao_valido,
        usuario=usuario_ativo,
    )

    cargo.refresh_from_db()

    documentos = list(
        DocumentoCargo.objects.filter(
            cargo=cargo,
        ).order_by("nome")
    )

    assert cargo.nome == "Eletricista atualizado"
    assert cargo.exige_documento is True
    assert cargo.status is False
    assert cargo.atualizado_por == usuario_ativo

    assert not DocumentoCargo.objects.filter(
        pk=documento_cargo.pk,
    ).exists()

    assert len(documentos) == 1
    assert documentos[0].nome == "Certificado NR-10 atualizado"

    assert documentos[0].criado_por == usuario_ativo
    assert documentos[0].atualizado_por == usuario_ativo

    assert [documento.uuid for documento in resultado["documentos"]] == [
        documento.uuid for documento in documentos
    ]
    assert resultado["uuid"] == cargo.uuid
    assert resultado["pk"] == cargo.pk


def test_atualizar_cargo_sem_alterar_documentos(
    cargo,
    documento_cargo,
    usuario_ativo,
):
    """Deve manter os documentos quando não forem informados."""
    repository = CargoRepository()

    resultado = repository.atualizar(
        cargo=cargo,
        dados={
            "nome": "Eletricista atualizado",
            "status": False,
        },
        usuario=usuario_ativo,
    )

    cargo.refresh_from_db()
    documento_cargo.refresh_from_db()

    assert cargo.nome == "Eletricista atualizado"
    assert cargo.status is False
    assert cargo.atualizado_por == usuario_ativo

    assert DocumentoCargo.objects.filter(
        pk=documento_cargo.pk,
        cargo=cargo,
    ).exists()

    assert resultado["documentos"] == [documento_cargo]
    assert resultado["uuid"] == cargo.uuid
    assert resultado["pk"] == cargo.pk


def test_atualizar_com_lista_vazia_deve_remover_documentos(
    cargo,
    documento_cargo,
    usuario_ativo,
):
    """Deve remover documentos quando uma lista vazia for informada."""
    repository = CargoRepository()

    resultado = repository.atualizar(
        cargo=cargo,
        dados={
            "exige_documento": False,
            "documentos": [],
        },
        usuario=usuario_ativo,
    )

    cargo.refresh_from_db()

    assert cargo.exige_documento is False
    assert cargo.atualizado_por == usuario_ativo

    assert not DocumentoCargo.objects.filter(
        cargo=cargo,
    ).exists()

    assert resultado["documentos"] == []
    assert resultado["uuid"] == cargo.uuid
    assert resultado["pk"] == cargo.pk


def test_atualizar_nao_deve_alterar_dados_originais(
    cargo,
    cargo_payload_atualizacao_valido,
    usuario_ativo,
):
    """Não deve modificar os dados recebidos na atualização."""
    repository = CargoRepository()

    dados = cargo_payload_atualizacao_valido
    dados_esperados = deepcopy(cargo_payload_atualizacao_valido)

    repository.atualizar(
        cargo=cargo,
        dados=dados,
        usuario=usuario_ativo,
    )

    assert dados == dados_esperados


def test_atualizar_nao_deve_persistir_cargo_invalido(
    cargo,
    usuario_ativo,
):
    """Não deve persistir a atualização de um cargo inválido."""
    repository = CargoRepository()

    with pytest.raises(ValidationError):
        repository.atualizar(
            cargo=cargo,
            dados={
                "nome": "",
            },
            usuario=usuario_ativo,
        )

    cargo.refresh_from_db()

    assert cargo.nome == "Eletricista"


def test_atualizar_deve_desfazer_transacao_com_documento_invalido(
    cargo,
    cargo_payload_atualizacao_valido,
    documento_cargo,
    usuario_ativo,
):
    """Deve restaurar cargo e documentos após falha de validação."""
    repository = CargoRepository()

    with pytest.raises(ValidationError):
        repository.atualizar(
            cargo=cargo,
            dados={
                **cargo_payload_atualizacao_valido,
                "documentos": [
                    {
                        "nome": "",
                    },
                ],
            },
            usuario=usuario_ativo,
        )

    cargo.refresh_from_db()
    documento_cargo.refresh_from_db()

    assert cargo.nome == "Eletricista"

    assert DocumentoCargo.objects.filter(
        pk=documento_cargo.pk,
        cargo=cargo,
        nome="Certificado NR-10",
    ).exists()

    assert not DocumentoCargo.objects.filter(
        cargo=cargo,
        nome="",
    ).exists()
