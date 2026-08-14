from unittest.mock import Mock, patch

import pytest

from apps.core.exceptions import AnexoArquivoError
from apps.core.repository.anexo_repository import AnexoRepository
from apps.usuarios.exceptions import UsuarioNaoEncontradoError
from apps.usuarios.models.usuario import Usuario

pytestmark = pytest.mark.django_db


def test_retorna_anexo_em_dicionario(anexo):
    """Verifica se converte o anexo para um dicionário."""
    resultado = AnexoRepository()._retorna_anexo_em_dicionario(anexo)

    assert resultado == {
        "uuid": str(anexo.uuid),
        "nome": "documento.pdf",
        "tipo": "documento",
        "tipo_mime": "application/pdf",
        "tamanho": 123,
        "url": "https://minio.local/documento.pdf",
    }


def test_consulta_por_uuid_retorna_anexo(anexo):
    """Verifica se busca o anexo pelo UUID."""
    manager = Mock()
    manager.get.return_value = anexo

    with patch(
        "apps.core.repository.anexo_repository.Anexo.objects",
        manager,
    ):
        assert AnexoRepository()._consulta_por_uuid("uuid") is anexo

    manager.get.assert_called_once_with(uuid="uuid")


def test_consulta_por_uuid_levanta_erro_quando_nao_encontra():
    """Verifica se lança erro quando o anexo não é encontrado."""
    manager = Mock()
    manager.get.side_effect = AnexoRepository().model.DoesNotExist

    with (
        patch(
            "apps.core.repository.anexo_repository.Anexo.objects",
            manager,
        ),
        pytest.raises(AnexoArquivoError) as exc_info,
    ):
        AnexoRepository()._consulta_por_uuid("uuid")

    assert exc_info.value.title == "Arquivo não encontrado."
    assert exc_info.value.detail == "Arquivo não foi encontrado."


def test_criar_nao_faz_upload_real_para_o_minio(anexo, usuario_ativo):
    """Verifica se cria o anexo sem realizar upload real no MinIO."""
    manager_usuario = Mock()
    manager_usuario.get.return_value = usuario_ativo
    manager_anexo = Mock()
    manager_anexo.create.return_value = anexo
    arquivo = Mock()

    with (
        patch(
            "apps.core.repository.anexo_repository.Usuario.objects",
            manager_usuario,
        ),
        patch(
            "apps.core.repository.anexo_repository.Anexo.objects",
            manager_anexo,
        ),
        patch(
            "apps.core.repository.anexo_repository.Anexo.arquivo.field.storage._save",
            autospec=True,
            return_value="arquivos/documento.pdf",
        ) as minio_save,
    ):
        resultado = AnexoRepository().criar(
            nome_original="documento.pdf",
            tipo="documento",
            tipo_mime="application/pdf",
            tamanho_bytes=10,
            arquivo=arquivo,
            usuario_id=usuario_ativo.pk,
        )

    assert resultado["uuid"] == anexo.uuid
    manager_anexo.create.assert_called_once_with(
        nome_original="documento.pdf",
        tipo="documento",
        tipo_mime="application/pdf",
        tamanho_bytes=10,
        arquivo=arquivo,
        criado_por=usuario_ativo,
    )
    minio_save.assert_not_called()


def test_criar_levanta_erro_quando_usuario_nao_existe():
    """Verifica se lança erro quando o usuário não existe."""
    manager = Mock()
    manager.get.side_effect = Usuario.DoesNotExist

    with (
        patch(
            "apps.core.repository.anexo_repository.Usuario.objects",
            manager,
        ),
        pytest.raises(UsuarioNaoEncontradoError) as exc_info,
    ):
        AnexoRepository().criar(
            nome_original="documento.pdf",
            tipo="documento",
            tipo_mime="application/pdf",
            tamanho_bytes=10,
            arquivo=Mock(),
            usuario_id=999,
        )

    assert exc_info.value.title == "Usuário não encontrado"
    assert exc_info.value.detail == (
        "O usuário responsável pelo anexo não foi encontrado."
    )


def test_buscar_por_uuid_delega_consulta(anexo):
    """Verifica se busca o anexo pelo UUID."""
    repository = AnexoRepository()
    with patch.object(
        repository,
        "_consulta_por_uuid",
        return_value=anexo,
    ):
        resultado = repository.buscar_por_uuid(anexo.uuid)

    assert resultado["nome"] == "documento.pdf"
    assert resultado["tamanho"] == 123


def test_listar_sem_filtro(anexo):
    """Verifica se lista todos os anexos sem filtro."""
    queryset = Mock()
    queryset.__iter__ = Mock(return_value=iter([anexo]))

    manager = Mock()
    manager.all.return_value = queryset

    with patch(
        "apps.core.repository.anexo_repository.Anexo.objects",
        manager,
    ):
        resultado = AnexoRepository().listar()

    assert resultado["arquivos"][0]["nome"] == "documento.pdf"
    manager.all.assert_called_once_with()
    queryset.filter.assert_not_called()


def test_listar_com_filtro():
    """Verifica se lista os anexos filtrando pelo tipo."""
    queryset_filtrado = Mock()
    queryset_filtrado.__iter__ = Mock(return_value=iter([]))

    queryset = Mock()
    queryset.filter.return_value = queryset_filtrado

    manager = Mock()
    manager.all.return_value = queryset

    with patch(
        "apps.core.repository.anexo_repository.Anexo.objects",
        manager,
    ):
        resultado = AnexoRepository().listar(tipo="documento")

    assert resultado == {"arquivos": []}
    queryset.filter.assert_called_once_with(tipo="documento")


def test_excluir_deleta_arquivo_e_registro(anexo):
    """Verifica se exclui o arquivo e o registro do anexo."""
    arquivo = Mock()
    anexo.arquivo = arquivo
    repository = AnexoRepository()

    with patch.object(
        repository,
        "_consulta_por_uuid",
        return_value=anexo,
    ):
        repository.excluir(anexo.uuid)

    arquivo.delete.assert_called_once_with(save=False)
    anexo.delete.assert_called_once_with()


def test_baixar_abre_arquivo(anexo):
    """Verifica se abre o arquivo para download."""
    repository = AnexoRepository()
    with patch.object(
        repository,
        "_consulta_por_uuid",
        return_value=anexo,
    ):
        resultado = repository.baixar(anexo.uuid)

    assert resultado == {
        "arquivo": "stream",
        "nome": "documento.pdf",
        "tipo_mime": "application/pdf",
    }
    anexo.arquivo.open.assert_called_once_with("rb")


def test_buscar_para_download(anexo):
    """Verifica se retorna os dados necessários para o download."""
    repository = AnexoRepository()
    with patch.object(
        repository,
        "_consulta_por_uuid",
        return_value=anexo,
    ):
        resultado = repository.buscar_para_download(anexo.uuid)

    assert resultado == {
        "arquivo": anexo.arquivo,
        "nome_original": "documento.pdf",
        "tipo_mime": "application/pdf",
    }
