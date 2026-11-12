"""Testes da logo da empresa."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from django.core.files.storage import InMemoryStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from apps.core.constants import TAMANHO_MAXIMO_ARQUIVO, TipoArquivo
from apps.empresa.models import Empresa, LogoEmpresa
from apps.empresa.repository.logo_repository import LogoEmpresaRepository
from apps.empresa.serializers.empresa_serializers import obter_url_logo
from apps.empresa.services.logo_service import LogoEmpresaService

pytestmark = pytest.mark.django_db

PNG = b"\x89PNG\r\n\x1a\n" + b"conteudo"
JPG = b"\xff\xd8\xff\xe0" + b"conteudo"
URL = "/api/v1/empresas/"


@pytest.fixture(autouse=True)
def storage_em_memoria() -> Iterator[InMemoryStorage]:
    """Evita acesso ao MinIO nos testes de logo."""
    storage = InMemoryStorage()
    campo = LogoEmpresa._meta.get_field("arquivo")
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


def _put(api_cliente, empresa, empresa_payload_valido, **extra):
    return api_cliente.put(
        f"{URL}{empresa.uuid}/",
        _dados(empresa_payload_valido, **extra),
        format="multipart",
    )


def _empresa_com_logo(api_cliente, empresa_payload_valido):
    resposta = _post(
        api_cliente,
        empresa_payload_valido,
        logo=SimpleUploadedFile("antiga.png", PNG),
    )
    assert resposta.status_code == status.HTTP_201_CREATED, resposta.content
    return Empresa.objects.get()


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
    registro = LogoEmpresa.objects.get()
    assert registro.empresa == Empresa.objects.get()
    assert registro.nome_original == nome
    assert registro.tipo == TipoArquivo.IMAGEM
    assert registro.tamanho_bytes == len(conteudo)
    assert registro.criado_por is not None
    assert registro.arquivo.name.startswith("empresas/logos/")
    assert nome.lower() not in registro.arquivo.name.lower()
    detalhe = api_cliente.get(f"{URL}{Empresa.objects.get().uuid}/").json()
    assert detalhe["logo_url"] == resposta.json()["logo_url"]


def test_cria_empresa_sem_logo(api_cliente, empresa_payload_valido):
    """A logo é opcional."""
    resposta = _post(api_cliente, empresa_payload_valido)

    assert resposta.status_code == status.HTTP_201_CREATED, resposta.content
    assert resposta.json()["logo_url"] is None
    assert not LogoEmpresa.objects.exists()


@pytest.mark.parametrize(
    ("nome", "conteudo"),
    [("logo.gif", b"GIF89a"), ("logo.docx", b"conteudo")],
    ids=["gif", "docx"],
)
def test_rejeita_extensao_invalida(
    api_cliente, empresa_payload_valido, nome, conteudo
):
    """Rejeita extensões fora de PNG, JPG e JPEG."""
    resposta = _post(
        api_cliente,
        empresa_payload_valido,
        logo=SimpleUploadedFile(nome, conteudo),
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert "logo" in resposta.json()
    assert not Empresa.objects.exists()


def test_rejeita_documento_pdf_como_logo(api_cliente, empresa_payload_valido):
    """PDF é aceito no core para anexos, mas a logo só admite imagens."""
    resposta = _post(
        api_cliente,
        empresa_payload_valido,
        logo=SimpleUploadedFile("logo.pdf", b"%PDF-1.4"),
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert not Empresa.objects.exists()


def test_rejeita_logo_acima_do_tamanho_maximo(
    api_cliente, empresa_payload_valido
):
    """Usa a validação de tamanho do core e devolve título e detalhe."""
    resposta = _post(
        api_cliente,
        empresa_payload_valido,
        logo=SimpleUploadedFile(
            "logo.png", PNG + b"0" * TAMANHO_MAXIMO_ARQUIVO
        ),
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json() == {
        "title": "Arquivo muito grande",
        "detail": "O arquivo não pode ultrapassar 2 MB.",
    }
    assert not Empresa.objects.exists()


def test_rejeita_logo_vazia(api_cliente, empresa_payload_valido):
    """Arquivo vazio é rejeitado pelo core."""
    resposta = _post(
        api_cliente,
        empresa_payload_valido,
        logo=SimpleUploadedFile("logo.png", b""),
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert not Empresa.objects.exists()


def test_edicao_substitui_logo_e_remove_arquivo_antigo(
    api_cliente,
    empresa_payload_valido,
    storage_em_memoria,
    django_capture_on_commit_callbacks,
):
    """Troca a logo, mantém uma única linha e apaga o arquivo anterior."""
    empresa = _empresa_com_logo(api_cliente, empresa_payload_valido)
    antiga = empresa.logo.arquivo.name

    with django_capture_on_commit_callbacks(execute=True):
        resposta = _put(
            api_cliente,
            empresa,
            empresa_payload_valido,
            logo=SimpleUploadedFile("nova.jpg", JPG),
        )

    assert resposta.status_code == status.HTTP_200_OK, resposta.content
    assert LogoEmpresa.objects.count() == 1
    nova = LogoEmpresa.objects.get()
    assert nova.nome_original == "nova.jpg"
    assert not storage_em_memoria.exists(antiga)
    assert storage_em_memoria.exists(nova.arquivo.name)
    assert resposta.json()["logo_url"]


def test_edicao_sem_logo_mantem_a_atual(
    api_cliente, empresa_payload_valido, storage_em_memoria
):
    """Não enviar o campo preserva a logo existente."""
    empresa = _empresa_com_logo(api_cliente, empresa_payload_valido)
    atual = empresa.logo.arquivo.name

    resposta = _put(api_cliente, empresa, empresa_payload_valido)

    assert resposta.status_code == status.HTTP_200_OK, resposta.content
    assert resposta.json()["logo_url"]
    assert LogoEmpresa.objects.get().arquivo.name == atual
    assert storage_em_memoria.exists(atual)


def test_edicao_com_logo_vazia_remove_a_logo(
    api_cliente,
    empresa_payload_valido,
    storage_em_memoria,
    django_capture_on_commit_callbacks,
):
    """Enviar o campo vazio remove a linha e o arquivo."""
    empresa = _empresa_com_logo(api_cliente, empresa_payload_valido)
    atual = empresa.logo.arquivo.name

    with django_capture_on_commit_callbacks(execute=True):
        resposta = _put(api_cliente, empresa, empresa_payload_valido, logo="")

    assert resposta.status_code == status.HTTP_200_OK, resposta.content
    assert resposta.json()["logo_url"] is None
    assert not LogoEmpresa.objects.exists()
    assert not storage_em_memoria.exists(atual)


def test_edicao_adiciona_logo_a_empresa_sem_logo(
    api_cliente, empresa_payload_valido, storage_em_memoria
):
    """Empresa sem logo anterior recebe a nova."""
    assert _post(api_cliente, empresa_payload_valido).status_code == 201
    empresa = Empresa.objects.get()

    resposta = _put(
        api_cliente,
        empresa,
        empresa_payload_valido,
        logo=SimpleUploadedFile("nova.png", PNG),
    )

    assert resposta.status_code == status.HTTP_200_OK, resposta.content
    assert storage_em_memoria.exists(LogoEmpresa.objects.get().arquivo.name)


def test_listagem_expoe_logo_url(api_cliente, empresa_payload_valido):
    """A listagem traz a URL da logo e None para empresas sem logo."""
    _empresa_com_logo(api_cliente, empresa_payload_valido)

    resposta = api_cliente.get(URL)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["results"][0]["logo_url"]


def test_logo_e_excluida_com_a_empresa(empresa, usuario_ativo):
    """A relação usa CASCADE: removendo a empresa, a logo some."""
    LogoEmpresa.objects.create(
        empresa=empresa,
        nome_original="logo.png",
        tipo=TipoArquivo.IMAGEM,
        arquivo=SimpleUploadedFile("logo.png", PNG),
        criado_por=usuario_ativo,
    )

    empresa.delete()

    assert not LogoEmpresa.objects.exists()


def test_str_do_modelo(empresa, usuario_ativo):
    """Representa a logo pelo nome da empresa."""
    logo = LogoEmpresa(empresa=empresa)

    assert str(logo) == f"Logo de {empresa.nome}"


def test_obter_url_logo_para_instancia_e_dicionario(empresa, usuario_ativo):
    """Cobre instância sem logo, com logo e dados já serializados."""
    assert obter_url_logo(empresa) is None
    assert obter_url_logo({"logo_url": None}) is None
    assert obter_url_logo({"logo_url": "https://x/logo.png"}) == (
        "https://x/logo.png"
    )

    LogoEmpresa.objects.create(
        empresa=empresa,
        nome_original="logo.png",
        tipo=TipoArquivo.IMAGEM,
        arquivo=SimpleUploadedFile("logo.png", PNG),
        criado_por=usuario_ativo,
    )
    empresa = Empresa.objects.select_related("logo").get(pk=empresa.pk)

    assert obter_url_logo(empresa)


class TestLogoEmpresaService:
    """Testes unitários do serviço da logo."""

    def test_sincronizar_valida_pelo_core_e_substitui(self):
        repository = MagicMock()
        repository.substituir.return_value = {"arquivo_url": "https://x/a.png"}
        anexo_service = MagicMock()
        anexo_service.validar_e_preparar_anexo.return_value = {
            "tipo": TipoArquivo.IMAGEM
        }
        usuario = MagicMock(id=7)
        arquivo = MagicMock()
        service = LogoEmpresaService(repository, anexo_service)

        url = service.sincronizar(1, arquivo, usuario)

        assert url == "https://x/a.png"
        anexo_service.validar_e_preparar_anexo.assert_called_once_with(
            arquivo=arquivo, id_usuario=7
        )
        repository.substituir.assert_called_once_with(
            1, {"tipo": TipoArquivo.IMAGEM}, usuario
        )

    def test_sincronizar_sem_usuario_repassa_none_ao_core(self):
        anexo_service = MagicMock()
        anexo_service.validar_e_preparar_anexo.return_value = {
            "tipo": TipoArquivo.IMAGEM
        }
        service = LogoEmpresaService(MagicMock(), anexo_service)

        service.sincronizar(1, MagicMock())

        assert (
            anexo_service.validar_e_preparar_anexo.call_args.kwargs[
                "id_usuario"
            ]
            is None
        )

    def test_sincronizar_com_none_remove_a_logo(self):
        repository = MagicMock()
        service = LogoEmpresaService(repository, MagicMock())

        assert service.sincronizar(1, None) is None
        repository.remover.assert_called_once_with(1)

    def test_obter_url_delega_ao_repositorio(self):
        repository = MagicMock()
        repository.obter_url.return_value = "https://x/a.png"

        assert LogoEmpresaService(repository).obter_url(1) == (
            "https://x/a.png"
        )

    def test_construtor_usa_dependencias_padrao(self):
        service = LogoEmpresaService()

        assert isinstance(service.repository, LogoEmpresaRepository)
        assert service.anexo_service is not None


def test_repositorio_obter_url(empresa, usuario_ativo):
    """Retorna None sem logo e a URL quando existe."""
    repository = LogoEmpresaRepository()
    assert repository.obter_url(empresa.id) is None

    LogoEmpresa.objects.create(
        empresa=empresa,
        nome_original="logo.png",
        tipo=TipoArquivo.IMAGEM,
        arquivo=SimpleUploadedFile("logo.png", PNG),
        criado_por=usuario_ativo,
    )

    assert repository.obter_url(empresa.id)


def test_edicao_rejeita_logo_invalida_e_mantem_a_atual(
    api_cliente, empresa_payload_valido, storage_em_memoria
):
    """Erro de arquivo na edição devolve 400 e não altera a logo atual."""
    empresa = _empresa_com_logo(api_cliente, empresa_payload_valido)
    atual = empresa.logo.arquivo.name

    resposta = _put(
        api_cliente,
        empresa,
        empresa_payload_valido,
        logo=SimpleUploadedFile(
            "grande.png", PNG + b"0" * TAMANHO_MAXIMO_ARQUIVO
        ),
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json()["title"] == "Arquivo muito grande"
    assert LogoEmpresa.objects.get().arquivo.name == atual
    assert storage_em_memoria.exists(atual)
