"""Testes do campo de logo da empresa."""

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.core.files.storage import InMemoryStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from apps.core.constants import TAMANHO_MAXIMO_ARQUIVO
from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.models import Empresa
from apps.empresa.serializers.empresa_serializers import obter_url_logo

pytestmark = pytest.mark.django_db

PNG = b"\x89PNG\r\n\x1a\n" + b"conteudo"
JPG = b"\xff\xd8\xff\xe0" + b"conteudo"
URL = "/api/v1/empresas/"


@pytest.fixture(autouse=True)
def storage_em_memoria() -> Iterator[InMemoryStorage]:
    """Evita acesso ao MinIO nos testes de logo."""
    storage = InMemoryStorage()
    campo = Empresa._meta.get_field("logo")
    with patch.object(campo, "storage", storage):
        yield storage


def _dados(empresa_payload_valido, **extra):
    """Monta um payload multipart de empresa com um responsável."""
    return {
        **empresa_payload_valido,
        "responsaveis_tecnicos[0]tipo": "preposto",
        "responsaveis_tecnicos[0]nome": "João Responsável",
        "responsaveis_tecnicos[0]email": "joao@email.com",
        "responsaveis_tecnicos[0]telefone": "11987654321",
        **extra,
    }


def _post(api_cliente, empresa_payload_valido, **extra):
    return api_cliente.post(
        URL, _dados(empresa_payload_valido, **extra), format="multipart"
    )


@pytest.mark.parametrize(
    ("nome", "conteudo"),
    [("logo.png", PNG), ("logo.jpg", JPG), ("LOGO.JPEG", JPG)],
)
def test_cria_empresa_com_logo(
    api_cliente, empresa_payload_valido, nome, conteudo
):
    """Aceita PNG, JPG e JPEG e devolve a URL da logo."""
    logo = SimpleUploadedFile(nome, conteudo, content_type="image/png")

    resposta = _post(api_cliente, empresa_payload_valido, logo=logo)

    assert resposta.status_code == status.HTTP_201_CREATED, resposta.content
    assert resposta.json()["logo_url"]
    empresa = Empresa.objects.get()
    assert empresa.logo.name.startswith("empresas/logos/")
    assert nome.lower() not in empresa.logo.name.lower()
    assert empresa.logo.name.endswith(nome.rsplit(".", 1)[1].lower())
    detalhe = api_cliente.get(f"{URL}{empresa.uuid}/").json()
    assert detalhe["logo_url"] == resposta.json()["logo_url"]


def test_cria_empresa_sem_logo(api_cliente, empresa_payload_valido):
    """A logo é opcional."""
    resposta = _post(api_cliente, empresa_payload_valido)

    assert resposta.status_code == status.HTTP_201_CREATED, resposta.content
    assert resposta.json()["logo_url"] is None
    assert not Empresa.objects.get().logo


@pytest.mark.parametrize(
    ("nome", "conteudo", "mensagem"),
    [
        (
            "logo.gif",
            b"GIF89a",
            EmpresaErrorMessages.LOGO_FORMATO_INVALIDO,
        ),
        (
            "logo.pdf",
            b"%PDF-1.4",
            EmpresaErrorMessages.LOGO_FORMATO_INVALIDO,
        ),
        (
            "logo.png",
            b"isto nao e uma imagem",
            EmpresaErrorMessages.LOGO_CONTEUDO_INVALIDO,
        ),
        (
            "logo.png",
            PNG + b"0" * TAMANHO_MAXIMO_ARQUIVO,
            EmpresaErrorMessages.LOGO_MUITO_GRANDE,
        ),
    ],
    ids=["gif", "pdf", "conteudo_falso", "muito_grande"],
)
def test_rejeita_logo_invalida(
    api_cliente, empresa_payload_valido, nome, conteudo, mensagem
):
    """Rejeita formato, conteúdo e tamanho inválidos."""
    logo = SimpleUploadedFile(nome, conteudo)

    resposta = _post(api_cliente, empresa_payload_valido, logo=logo)

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json()["logo"] == [mensagem]
    assert not Empresa.objects.exists()


def _empresa_com_logo(api_cliente, empresa_payload_valido):
    resposta = _post(
        api_cliente,
        empresa_payload_valido,
        logo=SimpleUploadedFile("antiga.png", PNG),
    )
    assert resposta.status_code == status.HTTP_201_CREATED, resposta.content
    return Empresa.objects.get()


def _put(api_cliente, empresa, empresa_payload_valido, **extra):
    return api_cliente.put(
        f"{URL}{empresa.uuid}/",
        _dados(empresa_payload_valido, **extra),
        format="multipart",
    )


def test_edicao_substitui_logo_e_remove_arquivo_antigo(
    api_cliente,
    empresa_payload_valido,
    storage_em_memoria,
    django_capture_on_commit_callbacks,
):
    """Troca a logo e apaga o arquivo anterior do storage."""
    empresa = _empresa_com_logo(api_cliente, empresa_payload_valido)
    antiga = empresa.logo.name

    with django_capture_on_commit_callbacks(execute=True):
        resposta = _put(
            api_cliente,
            empresa,
            empresa_payload_valido,
            logo=SimpleUploadedFile("nova.jpg", JPG),
        )

    assert resposta.status_code == status.HTTP_200_OK, resposta.content
    empresa.refresh_from_db()
    assert empresa.logo.name != antiga
    assert empresa.logo.name.endswith(".jpg")
    assert not storage_em_memoria.exists(antiga)
    assert storage_em_memoria.exists(empresa.logo.name)


def test_edicao_sem_logo_mantem_a_atual(
    api_cliente, empresa_payload_valido, storage_em_memoria
):
    """Não enviar o campo preserva a logo existente."""
    empresa = _empresa_com_logo(api_cliente, empresa_payload_valido)
    atual = empresa.logo.name

    resposta = _put(api_cliente, empresa, empresa_payload_valido)

    assert resposta.status_code == status.HTTP_200_OK, resposta.content
    assert resposta.json()["logo_url"]
    empresa.refresh_from_db()
    assert empresa.logo.name == atual
    assert storage_em_memoria.exists(atual)


def test_edicao_com_logo_vazia_remove_a_logo(
    api_cliente,
    empresa_payload_valido,
    storage_em_memoria,
    django_capture_on_commit_callbacks,
):
    """Enviar o campo vazio remove a logo e o arquivo."""
    empresa = _empresa_com_logo(api_cliente, empresa_payload_valido)
    atual = empresa.logo.name

    with django_capture_on_commit_callbacks(execute=True):
        resposta = _put(api_cliente, empresa, empresa_payload_valido, logo="")

    assert resposta.status_code == status.HTTP_200_OK, resposta.content
    assert resposta.json()["logo_url"] is None
    empresa.refresh_from_db()
    assert not empresa.logo
    assert not storage_em_memoria.exists(atual)


def test_edicao_adiciona_logo_a_empresa_sem_logo(
    api_cliente, empresa_payload_valido, storage_em_memoria
):
    """Empresa sem logo anterior recebe a nova sem tentar apagar nada."""
    assert _post(api_cliente, empresa_payload_valido).status_code == 201
    empresa = Empresa.objects.get()

    resposta = _put(
        api_cliente,
        empresa,
        empresa_payload_valido,
        logo=SimpleUploadedFile("nova.png", PNG),
    )

    assert resposta.status_code == status.HTTP_200_OK, resposta.content
    empresa.refresh_from_db()
    assert storage_em_memoria.exists(empresa.logo.name)


def test_modelo_valida_extensao_da_logo(empresa):
    """O modelo também rejeita extensões fora de PNG/JPG/JPEG."""
    empresa.logo = SimpleUploadedFile("logo.gif", b"GIF89a")

    with pytest.raises(ValidationError) as erro:
        empresa.full_clean()

    assert EmpresaErrorMessages.LOGO_FORMATO_INVALIDO in str(erro.value)


def test_obter_url_logo_aceita_instancia_e_dicionario(empresa):
    """Retorna None sem logo e a URL com logo, para instância e dicionário."""
    assert obter_url_logo(empresa) is None
    assert obter_url_logo({"logo": None}) is None

    empresa.logo = SimpleUploadedFile("logo.png", PNG)
    empresa.save()

    assert obter_url_logo(empresa)
    assert obter_url_logo({"logo": empresa.logo}) == obter_url_logo(empresa)
