from types import SimpleNamespace

import pytest

from apps.core.models import Anexo


def test_str_retorna_nome_original():
    """Verifica se retorna o nome original do arquivo."""
    anexo = Anexo(nome_original="documento.pdf")

    assert str(anexo) == "documento.pdf"


def test_nome_bucket_retorna_nome_do_arquivo():
    """Verifica se retorna o nome do arquivo armazenado no bucket."""
    anexo = Anexo()
    anexo.arquivo = SimpleNamespace(name="arquivos/uuid.pdf")

    assert anexo.nome_bucket == "arquivos/uuid.pdf"


def test_nome_bucket_rejeita_nome_inexistente():
    """Verifica se rejeita arquivo sem nome definido."""
    anexo = Anexo()
    anexo.arquivo = SimpleNamespace(name=None)

    with pytest.raises(
        ValueError, match="O nome do arquivo não está definido."
    ):
        _ = anexo.nome_bucket


def test_url_delega_para_o_storage():
    """Verifica se retorna a URL fornecida pelo storage."""
    anexo = Anexo()
    anexo.arquivo = SimpleNamespace(
        url="http://minio.local/arquivos/uuid.pdf",
    )

    assert anexo.url == "http://minio.local/arquivos/uuid.pdf"
