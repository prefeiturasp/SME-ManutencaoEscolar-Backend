"""Testes dos serializers da aplicação Cargo."""

import pytest

from apps.cargo.serializers import (
    CargoCriarSerializer,
    DocumentoCargoCriarSerializer,
)

pytestmark = pytest.mark.django_db


def test_validar_documento_do_cargo() -> None:
    """Deve validar os dados de um documento do cargo."""
    serializer = DocumentoCargoCriarSerializer(
        data={
            "nome": "Certificado NR-10",
        }
    )

    assert serializer.is_valid() is True
    assert serializer.validated_data["nome"] == "Certificado NR-10"


def test_rejeitar_documento_sem_nome() -> None:
    """Deve rejeitar um documento sem nome."""
    serializer = DocumentoCargoCriarSerializer(
        data={
            "nome": "",
        }
    )

    assert serializer.is_valid() is False
    assert "nome" in serializer.errors


def test_rejeitar_documento_com_nome_maior_que_limite() -> None:
    """Deve rejeitar documento cujo nome ultrapasse o limite."""
    serializer = DocumentoCargoCriarSerializer(
        data={
            "nome": "A" * 256,
        }
    )

    assert serializer.is_valid() is False
    assert "nome" in serializer.errors


def test_validar_cargo_que_exige_documentos() -> None:
    """Deve validar um cargo que exige e possui documentos."""
    serializer = CargoCriarSerializer(
        data={
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
    )

    assert serializer.is_valid() is True
    assert serializer.validated_data == {
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


def test_validar_cargo_que_nao_exige_documentos() -> None:
    """Deve validar um cargo que não exige documentos."""
    serializer = CargoCriarSerializer(
        data={
            "nome": "Auxiliar",
            "exige_documento": False,
            "status": True,
        }
    )

    assert serializer.is_valid() is True
    assert serializer.validated_data["nome"] == "Auxiliar"
    assert serializer.validated_data["exige_documento"] is False
    assert "documentos" not in serializer.validated_data


def test_rejeitar_cargo_que_exige_documento_sem_informar_documentos() -> None:
    """Deve exigir ao menos um documento quando configurado no cargo."""
    serializer = CargoCriarSerializer(
        data={
            "nome": "Eletricista",
            "exige_documento": True,
            "status": True,
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["documentos"] == [
        "Informe ao menos um documento para este cargo.",
    ]


def test_rejeitar_lista_vazia_quando_cargo_exige_documento() -> None:
    """Deve rejeitar lista vazia quando o cargo exige documento."""
    serializer = CargoCriarSerializer(
        data={
            "nome": "Eletricista",
            "exige_documento": True,
            "status": True,
            "documentos": [],
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["documentos"] == [
        "Informe ao menos um documento para este cargo.",
    ]


def test_rejeitar_documentos_quando_cargo_nao_os_exige() -> None:
    """Deve rejeitar documentos vinculados a um cargo que não os exige."""
    serializer = CargoCriarSerializer(
        data={
            "nome": "Auxiliar",
            "exige_documento": False,
            "status": True,
            "documentos": [
                {
                    "nome": "Documento pessoal",
                },
            ],
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["documentos"] == [
        (
            "Um cargo que não exige documentos não pode possuir "
            "documentos vinculados."
        ),
    ]


def test_considerar_que_cargo_nao_exige_documentos_por_padrao() -> None:
    """Deve considerar falsa a exigência quando ela não for informada."""
    serializer = CargoCriarSerializer(
        data={
            "nome": "Auxiliar",
            "status": True,
            "documentos": [
                {
                    "nome": "Documento pessoal",
                },
            ],
        }
    )

    assert serializer.is_valid() is False
    assert "documentos" in serializer.errors


def test_rejeitar_cargo_sem_nome() -> None:
    """Deve rejeitar o cadastro de um cargo sem nome."""
    serializer = CargoCriarSerializer(
        data={
            "exige_documento": False,
            "status": True,
        }
    )

    assert serializer.is_valid() is False
    assert "nome" in serializer.errors


def test_rejeitar_cargo_com_nome_maior_que_limite() -> None:
    """Deve rejeitar cargo cujo nome ultrapasse o limite."""
    serializer = CargoCriarSerializer(
        data={
            "nome": "A" * 256,
            "exige_documento": False,
            "status": True,
        }
    )

    assert serializer.is_valid() is False
    assert "nome" in serializer.errors


def test_rejeitar_cargo_com_documento_invalido() -> None:
    """Deve rejeitar um cargo quando um dos documentos for inválido."""
    serializer = CargoCriarSerializer(
        data={
            "nome": "Eletricista",
            "exige_documento": True,
            "status": True,
            "documentos": [
                {
                    "nome": "",
                },
            ],
        }
    )

    assert serializer.is_valid() is False
    assert "documentos" in serializer.errors
    assert "nome" in serializer.errors["documentos"][0]
