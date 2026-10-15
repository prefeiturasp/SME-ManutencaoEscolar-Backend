"""Testes dos repositórios do domínio Profissional."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.constants import TipoArquivo
from apps.profissional.models import (
    DocumentoFuncaoProfissional,
    FuncaoProfissional,
    Profissional,
)
from apps.profissional.repository.documento_funcao_repository import (
    DocumentoFuncaoProfissionalRepository,
)
from apps.profissional.repository.funcao_profissional_repository import (
    FuncaoProfissionalRepository,
)
from apps.profissional.repository.profissional_repository import (
    ProfissionalRepository,
)

pytestmark = pytest.mark.django_db


def test_profissional_repository_cria(usuario_ativo):
    """Persiste um profissional."""
    repository = ProfissionalRepository()
    resultado = repository.criar(
        {
            "nome": "José da Silva",
            "cpf": "12345678901",
            "rg": "123456789",
            "criado_por": usuario_ativo,
        }
    )
    profissional = Profissional.objects.get(pk=resultado["id"])

    assert resultado["nome"] == profissional.nome
    assert resultado["uuid"] == str(profissional.uuid)
    assert profissional.criado_por == usuario_ativo


def test_profissional_repository_deleta(usuario_ativo):
    """Exclui logicamente o profissional e registra o usuário responsável."""
    profissional = Profissional.objects.create(
        nome="José da Silva",
        cpf="12345678901",
        rg="123456789",
    )

    ProfissionalRepository().deletar(profissional, usuario_ativo)

    assert not Profissional.objects.filter(pk=profissional.pk).exists()
    profissional_excluido = Profissional.dm_objects.get(pk=profissional.pk)
    assert profissional_excluido.deletado_em is not None
    assert profissional_excluido.deletado_por == usuario_ativo


def test_funcao_repository_cria(cargo_profissional, usuario_ativo):
    """Persiste uma função profissional."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    repository = FuncaoProfissionalRepository()

    funcao = repository.criar(
        {
            "profissional": profissional,
            "cargo": cargo_profissional,
            "criado_por": usuario_ativo,
        }
    )
    funcao_persistida = FuncaoProfissional.objects.get(pk=funcao["id"])
    assert funcao["uuid"] == str(funcao_persistida.uuid)
    assert funcao_persistida.criado_por == usuario_ativo


def test_funcao_repository_lista_por_profissional(cargo_profissional):
    """Lista as funções do profissional em formato de dicionário."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )

    resultado = FuncaoProfissionalRepository().listar_por_profissional(
        profissional.id
    )

    assert resultado[0]["id"] == funcao.id
    assert resultado[0]["uuid"] == str(funcao.uuid)
    assert resultado[0]["cargo"] == cargo_profissional


def test_documento_repository_cria(cargo_profissional, usuario_ativo):
    """Persiste um documento de função."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    repository = DocumentoFuncaoProfissionalRepository()
    arquivo = SimpleUploadedFile(
        "NR10.pdf", b"conteudo", content_type="application/pdf"
    )

    documento = repository.criar(
        {
            "nome_original": "NR10.pdf",
            "arquivo": arquivo,
            "tipo": TipoArquivo.DOCUMENTO,
            "tipo_mime": "application/pdf",
            "tamanho_bytes": len(b"conteudo"),
            "funcao_profissional": funcao,
            "criado_por": usuario_ativo,
        }
    )
    documento_persistido = DocumentoFuncaoProfissional.objects.get(
        pk=documento["id"]
    )
    assert documento["uuid"] == str(documento_persistido.uuid)
    assert documento["nome_original"] == documento_persistido.nome_original
    assert documento["tipo"] == documento_persistido.tipo
    assert documento["tipo_mime"] == documento_persistido.tipo_mime
    assert documento["tamanho_bytes"] == documento_persistido.tamanho_bytes
    assert documento_persistido.criado_por == usuario_ativo


def test_documento_repository_lista_por_funcao(cargo_profissional):
    """Lista os documentos da função em formato de dicionário."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    documento = DocumentoFuncaoProfissional.objects.create(
        nome_original="NR10.pdf",
        arquivo=SimpleUploadedFile("NR10.pdf", b"conteudo"),
        tipo=TipoArquivo.DOCUMENTO,
        tipo_mime="application/pdf",
        tamanho_bytes=len(b"conteudo"),
        funcao_profissional=funcao,
    )

    resultado = DocumentoFuncaoProfissionalRepository().listar_por_funcao(
        funcao.id
    )

    assert resultado[0]["id"] == documento.id
    assert resultado[0]["uuid"] == str(documento.uuid)
    assert resultado[0]["nome_original"] == documento.nome_original


def test_funcao_repository_atualiza_sem_alteracoes(cargo_profissional):
    """Serializa a função sem executar uma atualização desnecessária."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )

    resultado = FuncaoProfissionalRepository().atualizar(
        funcao,
        {"uuid": funcao.uuid, "cargo": cargo_profissional},
    )

    assert resultado["id"] == funcao.id
    assert resultado["cargo"] == cargo_profissional


def test_funcao_repository_remove(cargo_profissional, usuario_ativo):
    """Remove logicamente uma função e registra o usuário responsável."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )

    FuncaoProfissionalRepository().remover(funcao, usuario_ativo)

    assert not FuncaoProfissional.objects.filter(pk=funcao.pk).exists()


def test_documento_repository_exclui_arquivo_apos_commit(
    cargo_profissional,
    django_capture_on_commit_callbacks,
):
    """Exclui o documento físico somente após confirmar a transação."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    documento = DocumentoFuncaoProfissional.objects.create(
        nome_original="NR10.pdf",
        arquivo=SimpleUploadedFile("NR10.pdf", b"conteudo"),
        tipo=TipoArquivo.DOCUMENTO,
        tipo_mime="application/pdf",
        tamanho_bytes=len(b"conteudo"),
        funcao_profissional=funcao,
    )
    nome_arquivo = documento.arquivo.name
    storage = documento.arquivo.storage

    with django_capture_on_commit_callbacks(execute=True):
        DocumentoFuncaoProfissionalRepository().excluir_nao_preservados(
            funcao.id, []
        )

    assert not DocumentoFuncaoProfissional.objects.filter(
        pk=documento.pk
    ).exists()
    assert not storage.exists(nome_arquivo)


def test_profissional_repository_verifica_duplicidade(usuario_ativo):
    """Informa se CPF e RG pertencem a outro profissional ativo."""
    existente = Profissional.objects.create(
        nome="Existente", cpf="12345678901", rg="123456789"
    )
    repository = ProfissionalRepository()

    assert repository.verificar_duplicidade("12345678901", "000") == (
        True,
        False,
    )
    assert repository.verificar_duplicidade("000", "123456789") == (
        False,
        True,
    )
    assert repository.verificar_duplicidade("12345678901", "123456789") == (
        True,
        True,
    )
    assert repository.verificar_duplicidade("000", "111") == (False, False)
    assert repository.verificar_duplicidade(
        "12345678901", "123456789", profissional_ignorado=existente
    ) == (False, False)


def test_profissional_repository_ignora_excluido_na_duplicidade(
    usuario_ativo,
):
    """Permite reutilizar CPF e RG de profissional excluído logicamente."""
    existente = Profissional.objects.create(
        nome="Existente", cpf="12345678901", rg="123456789"
    )
    existente.soft_delete(usuario=usuario_ativo)

    resultado = ProfissionalRepository().verificar_duplicidade(
        "12345678901", "123456789"
    )

    assert resultado == (False, False)
