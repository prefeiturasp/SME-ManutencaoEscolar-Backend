from unittest.mock import Mock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.constants import (
    MAPA_EXTENSOES_TIPO_ARQUIVO,
    TAMANHO_MAXIMO_ARQUIVO,
)
from apps.core.exceptions import AnexoArquivoError
from apps.usuarios.exceptions import UsuarioNaoEncontradoError

pytestmark = pytest.mark.django_db


def test_enviar_arquivo_valido_prepara_metadados_e_delega_ao_repository(
    mock_repository_anexo, arquivo, usuario_ativo, anexo_service
):
    """Verifica se prepara os metadados e delega a criação ao repository."""
    upload = arquivo

    with (
        patch(
            "apps.core.services.anexo_service.UsuarioRepository."
            "usuario_existe_por_id",
            return_value=True,
        ),
        patch.object(
            anexo_service,
            "_gerar_nome_arquivo",
            return_value="uuid-gerado.pdf",
        ),
    ):
        resultado = anexo_service.enviar_arquivo(
            upload, id_usuario=usuario_ativo.pk
        )

    assert resultado == mock_repository_anexo.criar.return_value
    assert upload.name == "uuid-gerado.pdf"
    mock_repository_anexo.criar.assert_called_once_with(
        nome_original="documento.pdf",
        tipo=MAPA_EXTENSOES_TIPO_ARQUIVO[".pdf"],
        tipo_mime="application/pdf",
        tamanho_bytes=8,
        arquivo=upload,
        usuario_id=usuario_ativo.pk,
    )


def test_enviar_arquivo_nao_envia_quando_usuario_nao_existe(
    anexo_service, mock_repository_anexo, arquivo
):
    """Verifica se rejeita o envio quando o usuário não existe."""
    with (
        patch(
            "apps.core.services.anexo_service.UsuarioRepository."
            "usuario_existe_por_id",
            return_value=False,
        ),
        pytest.raises(UsuarioNaoEncontradoError),
    ):
        anexo_service.enviar_arquivo(arquivo, id_usuario=999)

    mock_repository_anexo.criar.assert_not_called()


@pytest.mark.parametrize(
    "upload, titulo, detalhe",
    [
        (
            None,
            "Arquivo não informado",
            "Nenhum arquivo foi informado.",
        ),
        (
            SimpleUploadedFile(
                "vazio.pdf", b"", content_type="application/pdf"
            ),
            "Arquivo vazio",
            "Não é permitido enviar um arquivo vazio.",
        ),
    ],
)
def test_enviar_arquivo_rejeita_arquivo_invalido(
    anexo_service,
    mock_repository_anexo,
    upload,
    titulo,
    detalhe,
):
    """Verifica se rejeita arquivo ausente ou vazio."""
    with (
        patch(
            "apps.core.services.anexo_service.UsuarioRepository."
            "usuario_existe_por_id",
            return_value=True,
        ),
        pytest.raises(AnexoArquivoError) as exc_info,
    ):
        anexo_service.enviar_arquivo(upload, id_usuario=10)

    assert exc_info.value.title == titulo
    assert exc_info.value.detail == detalhe
    mock_repository_anexo.criar.assert_not_called()


def test_enviar_arquivo_rejeita_nome_ausente(
    anexo_service, mock_repository_anexo, arquivo
):
    """Verifica se rejeita arquivo sem nome."""
    upload = arquivo
    upload.name = None

    with (
        patch(
            "apps.core.services.anexo_service.UsuarioRepository."
            "usuario_existe_por_id",
            return_value=True,
        ),
        pytest.raises(AnexoArquivoError) as exc_info,
    ):
        anexo_service.enviar_arquivo(upload, id_usuario=10)

    assert exc_info.value.title == "Nome do arquivo ausente"
    mock_repository_anexo.criar.assert_not_called()


def test_enviar_arquivo_rejeita_tamanho_indisponivel(
    anexo_service, mock_repository_anexo, arquivo
):
    """Verifica se rejeita arquivo sem tamanho definido."""
    upload = arquivo
    upload.size = None

    with (
        patch(
            "apps.core.services.anexo_service.UsuarioRepository."
            "usuario_existe_por_id",
            return_value=True,
        ),
        pytest.raises(AnexoArquivoError) as exc_info,
    ):
        anexo_service.enviar_arquivo(upload, id_usuario=10)

    assert exc_info.value.title == "Tamanho do arquivo indisponível"
    mock_repository_anexo.criar.assert_not_called()


def test_enviar_arquivo_rejeita_arquivo_maior_que_limite(
    anexo_service, mock_repository_anexo, arquivo
):
    """Verifica se rejeita arquivo maior que o limite permitido."""
    upload = SimpleUploadedFile(
        "documento.pdf",
        b"x" * (TAMANHO_MAXIMO_ARQUIVO + 1),
        content_type="application/pdf",
    )

    with (
        patch(
            "apps.core.services.anexo_service.UsuarioRepository."
            "usuario_existe_por_id",
            return_value=True,
        ),
        pytest.raises(AnexoArquivoError) as exc_info,
    ):
        anexo_service.enviar_arquivo(upload, id_usuario=10)

    assert exc_info.value.title == "Arquivo muito grande"
    assert exc_info.value.detail == "O arquivo não pode ultrapassar 2 MB."
    mock_repository_anexo.criar.assert_not_called()


def test_enviar_arquivo_rejeita_extensao_nao_permitida(
    anexo_service, mock_repository_anexo, arquivo
):
    """Verifica se rejeita arquivo com extensão não permitida."""
    upload = SimpleUploadedFile(
        "documento.exe",
        b"conteudo",
        content_type="application/octet-stream",
    )

    with (
        patch(
            "apps.core.services.anexo_service.UsuarioRepository."
            "usuario_existe_por_id",
            return_value=True,
        ),
        pytest.raises(AnexoArquivoError) as exc_info,
    ):
        anexo_service.enviar_arquivo(upload, id_usuario=10)

    assert exc_info.value.title == "Tipo de arquivo não permitido"
    mock_repository_anexo.criar.assert_not_called()


def test_salvar_remove_caminho_do_nome_e_inferir_mime(
    anexo_service, mock_repository_anexo
):
    """Verifica se normaliza o nome e identifica o MIME do arquivo."""
    upload = SimpleUploadedFile("arquivo.pdf", b"conteudo")
    upload.content_type = None

    with patch.object(
        anexo_service,
        "_gerar_nome_arquivo",
        return_value="uuid-gerado.pdf",
    ):
        anexo_service._salvar(
            arquivo=upload,
            tipo=MAPA_EXTENSOES_TIPO_ARQUIVO[".pdf"],
            nome_original="/caminho/arquivo.pdf",
            tamanho_bytes=9,
            id_usuario=10,
        )

    mock_repository_anexo.criar.assert_called_once_with(
        nome_original="arquivo.pdf",
        tipo=MAPA_EXTENSOES_TIPO_ARQUIVO[".pdf"],
        tipo_mime="application/pdf",
        tamanho_bytes=9,
        arquivo=upload,
        usuario_id=10,
    )


@pytest.mark.parametrize(
    ("nome", "esperado"),
    [
        ("arquivo.PDF", ".pdf"),
        ("arquivo.txt", ".txt"),
        ("sem_extensao", ""),
    ],
)
def test_obter_extensao_normaliza_para_minusculas(
    nome: str, esperado: str, anexo_service
):
    """Verifica se normaliza a extensão do arquivo."""
    assert anexo_service._obter_extensao(nome) == esperado


def test_gerar_nome_arquivo_preserva_extensao(anexo_service):
    """Verifica se gera nome único preservando a extensão."""
    with patch(
        "apps.core.services.anexo_service.uuid.uuid4",
        return_value="uuid-fixo",
    ):
        assert (
            anexo_service._gerar_nome_arquivo("arquivo.PDF") == "uuid-fixo.pdf"
        )


def test_buscar_por_uuid_propaga_erro_com_novo_contexto(anexo_service):
    """Verifica se propaga o erro ao buscar um anexo pelo UUID."""
    erro = AnexoArquivoError(
        title="Arquivo não encontrado.",
        detail="Arquivo não foi encontrado.",
    )
    anexo_service.repository.buscar_por_uuid.side_effect = erro

    with pytest.raises(AnexoArquivoError) as exc_info:
        anexo_service.buscar_por_uuid("uuid")

    assert exc_info.value.title == erro.title
    assert exc_info.value.detail == erro.detail


def test_listar_delega_ao_repository(anexo_service):
    """Verifica se delega a listagem de anexos ao repository."""
    anexo_service.repository.listar.return_value = {"arquivos": []}

    assert anexo_service.listar("documento") == {"arquivos": []}
    anexo_service.repository.listar.assert_called_once_with(tipo="documento")


def test_excluir_delega_ao_repository(anexo_service):
    """Verifica se delega a exclusão do anexo ao repository."""
    anexo_service.excluir("uuid")
    anexo_service.repository.excluir.assert_called_once_with("uuid")


def test_obter_url_retorna_url(anexo_service):
    """Verifica se retorna a URL do anexo."""
    anexo_service.repository.buscar_por_uuid.return_value = {
        "nome": "documento.pdf",
        "url": "https://minio.local/documento.pdf",
    }

    assert (
        anexo_service.obter_url("uuid") == "https://minio.local/documento.pdf"
    )


def test_obter_url_rejeita_anexo_sem_url(anexo_service):
    """Verifica se rejeita anexo sem URL válida."""
    anexo_service.repository.buscar_por_uuid.return_value = {
        "nome": "documento.pdf",
        "url": None,
    }

    with pytest.raises(AnexoArquivoError) as exc_info:
        anexo_service.obter_url("uuid")

    assert exc_info.value.title == "URL inválida."


def test_obter_para_download_delega_ao_repository(anexo_service):
    """Verifica se busca os dados para download no repository."""
    identificador = "12345678-1234-5678-1234-567812345678"
    resultado_esperado = {
        "arquivo": Mock(),
        "nome_original": "documento.pdf",
        "tipo_mime": "application/pdf",
    }

    anexo_service.repository.buscar_para_download.return_value = (
        resultado_esperado
    )

    resultado = anexo_service.obter_para_download(identificador)

    assert resultado == resultado_esperado
    anexo_service.repository.buscar_para_download.assert_called_once_with(
        identificador
    )
