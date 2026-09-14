"""Testes dos modelos da aplicação Cargo."""

import pytest
from django.db import IntegrityError, transaction

from apps.cargo.models import Cargo, DocumentoCargo

pytestmark = pytest.mark.django_db


def test_criar_cargo_com_valores_informados() -> None:
    """Deve criar um cargo com os valores informados."""
    cargo = Cargo.objects.create(
        nome="Eletricista",
        exige_documento=True,
        status=False,
    )

    assert cargo.pk is not None
    assert cargo.nome == "Eletricista"
    assert cargo.exige_documento is True
    assert cargo.status is False


def test_criar_cargo_com_valores_padrao() -> None:
    """Deve criar um cargo com os valores padrão."""
    cargo = Cargo.objects.create(nome="Encanador")

    assert cargo.exige_documento is False
    assert cargo.status is True


def test_retornar_nome_do_cargo_como_representacao_textual() -> None:
    """Deve retornar o nome do cargo como representação textual."""
    cargo = Cargo(nome="Engenheiro")

    assert str(cargo) == "Engenheiro"


def test_nao_permitir_cargos_ativos_com_nomes_iguais() -> None:
    """Não deve permitir cargos ativos com nomes iguais."""
    Cargo.objects.create(nome="Eletricista")

    with pytest.raises(IntegrityError), transaction.atomic():
        Cargo.objects.create(nome="Eletricista")


def test_nao_permitir_cargos_com_nomes_iguais_ignorando_maiusculas() -> None:
    """Não deve permitir nomes iguais ignorando maiúsculas e minúsculas."""
    Cargo.objects.create(nome="Eletricista")

    with pytest.raises(IntegrityError), transaction.atomic():
        Cargo.objects.create(nome="ELETRICISTA")


def test_ordenar_cargos_por_status_e_id_decrescente() -> None:
    """Deve ordenar cargos por status e ID em ordem decrescente."""
    cargo_inativo = Cargo.objects.create(
        nome="Cargo inativo",
        status=False,
    )
    primeiro_cargo_ativo = Cargo.objects.create(
        nome="Primeiro cargo ativo",
        status=True,
    )
    segundo_cargo_ativo = Cargo.objects.create(
        nome="Segundo cargo ativo",
        status=True,
    )

    cargos = list(Cargo.objects.all())

    assert cargos == [
        segundo_cargo_ativo,
        primeiro_cargo_ativo,
        cargo_inativo,
    ]


def test_configurar_nomes_amigaveis_do_model_cargo() -> None:
    """Deve configurar os nomes amigáveis do modelo Cargo."""
    assert Cargo._meta.verbose_name == "Cargo"
    assert Cargo._meta.verbose_name_plural == "Cargos"


def test_criar_documento_vinculado_ao_cargo() -> None:
    """Deve criar um documento vinculado ao cargo."""
    cargo = Cargo.objects.create(
        nome="Eletricista",
        exige_documento=True,
    )
    documento = DocumentoCargo.objects.create(
        nome="Certificado NR-10",
        cargo=cargo,
    )

    assert documento.pk is not None
    assert documento.nome == "Certificado NR-10"
    assert documento.cargo == cargo
    assert documento.cargo_id == cargo.pk


def test_retornar_nome_do_documento_como_representacao_textual() -> None:
    """Deve retornar o nome do documento como representação textual."""
    cargo = Cargo(nome="Eletricista")
    documento = DocumentoCargo(
        nome="Certificado NR-10",
        cargo=cargo,
    )

    assert str(documento) == "Certificado NR-10"


def test_acessar_documentos_pelo_cargo() -> None:
    """Deve acessar os documentos usando o relacionamento do cargo."""
    cargo = Cargo.objects.create(
        nome="Eletricista",
        exige_documento=True,
    )
    primeiro_documento = DocumentoCargo.objects.create(
        nome="Certificado NR-10",
        cargo=cargo,
    )
    segundo_documento = DocumentoCargo.objects.create(
        nome="Documento pessoal",
        cargo=cargo,
    )

    documentos = list(cargo.documentos.all())

    assert documentos == [
        primeiro_documento,
        segundo_documento,
    ]


def test_nao_permitir_documentos_iguais_no_mesmo_cargo() -> None:
    """Não deve permitir documentos com nomes iguais no mesmo cargo."""
    cargo = Cargo.objects.create(
        nome="Eletricista",
        exige_documento=True,
    )
    DocumentoCargo.objects.create(
        nome="Certificado NR-10",
        cargo=cargo,
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        DocumentoCargo.objects.create(
            nome="Certificado NR-10",
            cargo=cargo,
        )


def test_nao_permitir_documentos_iguais_ignorando_maiusculas() -> None:
    """Não deve permitir nomes iguais, independentemente de maiúsculas."""
    cargo = Cargo.objects.create(
        nome="Eletricista",
        exige_documento=True,
    )
    DocumentoCargo.objects.create(
        nome="Certificado NR-10",
        cargo=cargo,
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        DocumentoCargo.objects.create(
            nome="CERTIFICADO NR-10",
            cargo=cargo,
        )


def test_permitir_documento_com_mesmo_nome_em_cargos_diferentes() -> None:
    """Deve permitir documentos com o mesmo nome em cargos diferentes."""
    primeiro_cargo = Cargo.objects.create(
        nome="Eletricista",
        exige_documento=True,
    )
    segundo_cargo = Cargo.objects.create(
        nome="Engenheiro",
        exige_documento=True,
    )
    primeiro_documento = DocumentoCargo.objects.create(
        nome="Documento pessoal",
        cargo=primeiro_cargo,
    )
    segundo_documento = DocumentoCargo.objects.create(
        nome="Documento pessoal",
        cargo=segundo_cargo,
    )

    assert primeiro_documento.pk is not None
    assert segundo_documento.pk is not None
    assert primeiro_documento.cargo != segundo_documento.cargo


def test_ordenar_documentos_por_nome() -> None:
    """Deve ordenar os documentos pelo nome."""
    cargo = Cargo.objects.create(
        nome="Eletricista",
        exige_documento=True,
    )
    documento_rg = DocumentoCargo.objects.create(
        nome="RG",
        cargo=cargo,
    )
    documento_certificado = DocumentoCargo.objects.create(
        nome="Certificado",
        cargo=cargo,
    )

    documentos = list(DocumentoCargo.objects.all())

    assert documentos == [
        documento_certificado,
        documento_rg,
    ]


def test_configurar_nomes_amigaveis_do_documento() -> None:
    """Deve configurar os nomes amigáveis de DocumentoCargo."""
    assert DocumentoCargo._meta.verbose_name == "Documento do cargo"
    assert DocumentoCargo._meta.verbose_name_plural == "Documentos dos cargos"
