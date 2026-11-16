"""Testes da migração que cria os documentos exigidos das funções."""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = pytest.mark.django_db(transaction=True)

ANTES = [("profissional", "0003_documentofuncaoprofissional_nome_documento")]
DEPOIS = [("profissional", "0004_documento_exigido_funcao")]


def _migrar(alvo):
    """Leva o banco até a migração informada e devolve o estado."""
    executor = MigrationExecutor(connection)
    executor.migrate(alvo)
    executor.loader.build_graph()
    return executor.loader.project_state(alvo).apps


def _preparar(apps, cargo_nome, cpf, anexos, cargo_docs, alterado):
    """Cria cargo, profissional, função e anexos no estado antigo."""
    from django.utils import timezone

    Cargo = apps.get_model("cargo", "Cargo")
    DocumentoCargo = apps.get_model("cargo", "DocumentoCargo")
    Profissional = apps.get_model("profissional", "Profissional")
    funcao_modelo = apps.get_model("profissional", "FuncaoProfissional")
    anexo_modelo = apps.get_model(
        "profissional", "DocumentoFuncaoProfissional"
    )

    cargo = Cargo.objects.create(nome=cargo_nome, exige_documento=True)
    for nome in cargo_docs:
        DocumentoCargo.objects.create(cargo=cargo, nome=nome)
    profissional = Profissional.objects.create(
        nome="José", cpf=cpf, rg=cpf[:9]
    )
    funcao = funcao_modelo.objects.create(
        profissional=profissional, cargo=cargo
    )
    for nome_original, nome_documento in anexos:
        anexo_modelo.objects.create(
            funcao_profissional=funcao,
            arquivo="x.pdf",
            nome_original=nome_original,
            nome_documento=nome_documento,
        )
    data = (
        timezone.now() + timezone.timedelta(days=1)
        if alterado
        else funcao.criado_em
    )
    Cargo.objects.filter(pk=cargo.pk).update(atualizado_em=data)
    return funcao.pk


def _nomes(apps, funcao_pk):
    """Lista os documentos exigidos da função, na ordem."""
    exigido_modelo = apps.get_model("profissional", "DocumentoExigidoFuncao")
    return list(
        exigido_modelo.objects.filter(funcao_profissional_id=funcao_pk)
        .order_by("ordem")
        .values_list("nome", flat=True)
    )


def test_backfill_cobre_todos_os_cenarios():
    """Usa o nome gravado, o cargo inalterado ou o nome do arquivo."""
    antigo = _migrar(ANTES)
    com_nome = _preparar(
        antigo,
        "A",
        "11111111111",
        [("a.pdf", "Senai"), ("b.pdf", "RG")],
        ["RG", "Senai"],
        True,
    )
    inalterado = _preparar(
        antigo,
        "B",
        "22222222222",
        [("um.pdf", ""), ("dois.pdf", "")],
        ["Zeta", "Alfa"],
        False,
    )
    alterado = _preparar(
        antigo,
        "C",
        "33333333333",
        [("rg.pdf", ""), ("rg.pdf", "")],
        ["RG", "CPF"],
        True,
    )
    sem_anexo = _preparar(antigo, "D", "44444444444", [], [], False)

    novo = _migrar(DEPOIS)

    assert _nomes(novo, com_nome) == ["Senai", "RG"]
    assert _nomes(novo, inalterado) == ["Alfa", "Zeta"]
    assert _nomes(novo, alterado) == ["rg.pdf", "rg.pdf (2)"]
    assert _nomes(novo, sem_anexo) == []
    anexo_modelo = novo.get_model(
        "profissional", "DocumentoFuncaoProfissional"
    )
    assert not anexo_modelo.objects.filter(
        documento_exigido__isnull=True
    ).exists()


def test_reversao_devolve_o_nome_ao_anexo():
    """Voltar a migração restaura o campo nome_documento."""
    antigo = _migrar(ANTES)
    funcao = _preparar(
        antigo, "E", "55555555555", [("a.pdf", "Senai")], ["Senai"], True
    )
    _migrar(DEPOIS)

    revertido = _migrar(ANTES)

    anexo_modelo = revertido.get_model(
        "profissional", "DocumentoFuncaoProfissional"
    )
    assert anexo_modelo.objects.get(
        funcao_profissional_id=funcao
    ).nome_documento == ("Senai")
    _migrar(DEPOIS)
