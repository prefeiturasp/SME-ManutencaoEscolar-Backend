"""Testes dos serviços do domínio Profissional."""

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.cargo.models import Cargo
from apps.core.constants import TipoArquivo
from apps.profissional.constants import ProfissionalErrorMessages
from apps.profissional.models import (
    DocumentoFuncaoProfissional,
    FuncaoProfissional,
    Profissional,
)
from apps.profissional.services.documento_funcao_services import (
    DocumentoFuncaoProfissionalService,
)
from apps.profissional.services.funcao_profissional_services import (
    FuncaoProfissionalService,
)
from apps.profissional.services.profissional_services import (
    ProfissionalService,
)

pytestmark = pytest.mark.django_db


def criar_profissional(sufixo: str = "") -> Profissional:
    """Cria um profissional persistido com documentos únicos."""
    return Profissional.objects.create(
        nome=f"José da Silva{sufixo}",
        cpf=f"123456789{sufixo:0>2}",
        rg=f"987654321{sufixo}",
    )


def criar_documento(
    funcao: FuncaoProfissional,
    nome: str,
) -> DocumentoFuncaoProfissional:
    """Cria um documento persistido para uma função profissional."""
    conteudo = b"conteudo"
    return DocumentoFuncaoProfissional.objects.create(
        nome_original=nome,
        arquivo=SimpleUploadedFile(nome, conteudo),
        tipo=TipoArquivo.DOCUMENTO,
        tipo_mime="application/pdf",
        tamanho_bytes=len(conteudo),
        funcao_profissional=funcao,
    )


def test_documento_service_valida_e_cria_documentos(
    cargo_profissional,
    usuario_ativo,
):
    """Valida o arquivo e persiste o documento com seus metadados."""
    profissional = criar_profissional()
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    arquivo = SimpleUploadedFile(
        "nr10.pdf", b"conteudo", content_type="application/pdf"
    )

    resultado = DocumentoFuncaoProfissionalService().sincronizar(
        funcao.id, [{"arquivo": arquivo}], usuario_ativo
    )

    documento = DocumentoFuncaoProfissional.objects.get(
        funcao_profissional=funcao
    )
    assert resultado[0]["uuid"] == str(documento.uuid)
    assert documento.nome_original == "nr10.pdf"
    assert documento.tipo == TipoArquivo.DOCUMENTO
    assert documento.tipo_mime == "application/pdf"
    assert documento.tamanho_bytes == len(b"conteudo")
    assert documento.criado_por == usuario_ativo


def test_documento_service_preserva_existentes_e_exclui_ausentes(
    cargo_profissional,
):
    """Preserva os UUIDs informados e remove documentos omitidos."""
    profissional = criar_profissional()
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    preservado = criar_documento(funcao, "preservado.pdf")
    ausente = criar_documento(funcao, "ausente.pdf")

    resultado = DocumentoFuncaoProfissionalService().sincronizar(
        funcao.id, [{"uuid": str(preservado.uuid)}]
    )

    assert resultado == []
    assert DocumentoFuncaoProfissional.objects.filter(
        pk=preservado.pk
    ).exists()
    assert not DocumentoFuncaoProfissional.objects.filter(
        pk=ausente.pk
    ).exists()


def test_documento_service_rejeita_uuid_de_outra_funcao(
    cargo_profissional,
):
    """Impede preservar documento que não pertence à função."""
    profissional = criar_profissional()
    outro_cargo = Cargo.objects.create(nome="Encanador")
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    outra_funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=outro_cargo
    )
    documento = criar_documento(outra_funcao, "outro.pdf")

    with pytest.raises(ValidationError) as exc_info:
        DocumentoFuncaoProfissionalService().sincronizar(
            funcao.id, [{"uuid": str(documento.uuid)}]
        )

    assert exc_info.value.message_dict == {
        "documentos": [
            ProfissionalErrorMessages.DOCUMENTO_FUNCAO_NAO_ENCONTRADO
        ]
    }
    assert DocumentoFuncaoProfissional.objects.filter(pk=documento.pk).exists()


def test_funcao_service_cria_funcao_e_documentos(
    cargo_profissional,
    usuario_ativo,
):
    """Cria uma função e persiste seus documentos."""
    profissional = criar_profissional()
    arquivo = SimpleUploadedFile(
        "novo.pdf", b"conteudo", content_type="application/pdf"
    )

    resultado = FuncaoProfissionalService().sincronizar(
        profissional.id,
        [{"cargo": cargo_profissional, "documentos": [{"arquivo": arquivo}]}],
        usuario_ativo,
    )

    funcao = FuncaoProfissional.objects.get(profissional=profissional)
    documento = DocumentoFuncaoProfissional.objects.get(
        funcao_profissional=funcao
    )
    assert resultado[0]["id"] == funcao.id
    assert resultado[0]["documentos"][0]["id"] == documento.id
    assert funcao.criado_por == usuario_ativo
    assert documento.criado_por == usuario_ativo


def test_funcao_service_exige_documento_quando_configurado():
    """Impede função sem documento quando o cargo o exige."""
    profissional = criar_profissional()
    cargo = Cargo.objects.create(nome="Eletricista", exige_documento=True)

    with pytest.raises(ValidationError) as exc_info:
        FuncaoProfissionalService().sincronizar(
            profissional.id, [{"cargo": cargo}]
        )

    assert exc_info.value.message_dict == {
        "documentos": [
            ProfissionalErrorMessages.DOCUMENTOS_FUNCAO_PROFISSIONAL_OBRIGATORIOS
        ]
    }
    assert not FuncaoProfissional.objects.filter(
        profissional=profissional
    ).exists()


def test_funcao_service_sincroniza_por_uuid_e_remove_ausentes(
    cargo_profissional,
    usuario_ativo,
):
    """Atualiza por UUID, cria novas funções e remove as ausentes."""
    profissional = criar_profissional()
    cargo_ausente = Cargo.objects.create(nome="Encanador")
    cargo_novo = Cargo.objects.create(nome="Pedreiro")
    funcao_existente = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    funcao_ausente = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_ausente
    )
    documento = criar_documento(funcao_existente, "existente.pdf")

    resultado = FuncaoProfissionalService().sincronizar(
        profissional.id,
        [
            {
                "uuid": str(funcao_existente.uuid),
                "cargo": cargo_profissional,
                "documentos": [{"uuid": str(documento.uuid)}],
            },
            {"cargo": cargo_novo, "documentos": []},
        ],
        usuario_ativo,
    )

    assert [item["cargo"] for item in resultado] == [
        cargo_profissional,
        cargo_novo,
    ]
    assert resultado[0]["documentos"] == []
    assert FuncaoProfissional.objects.filter(pk=funcao_existente.pk).exists()
    assert not FuncaoProfissional.objects.filter(pk=funcao_ausente.pk).exists()
    assert FuncaoProfissional.objects.filter(
        profissional=profissional,
        cargo=cargo_novo,
        criado_por=usuario_ativo,
    ).exists()
    assert DocumentoFuncaoProfissional.objects.filter(pk=documento.pk).exists()


def test_funcao_service_rejeita_uuid_de_outro_profissional(
    cargo_profissional,
):
    """Impede a sincronização de função alheia ao profissional."""
    profissional = criar_profissional()
    outro_profissional = criar_profissional("2")
    funcao_alheia = FuncaoProfissional.objects.create(
        profissional=outro_profissional, cargo=cargo_profissional
    )

    with pytest.raises(ValidationError) as exc_info:
        FuncaoProfissionalService().sincronizar(
            profissional.id,
            [{"uuid": str(funcao_alheia.uuid), "cargo": cargo_profissional}],
        )

    assert exc_info.value.message_dict == {
        "funcoes": [
            ProfissionalErrorMessages.FUNCAO_PROFISSIONAL_NAO_ENCONTRADA
        ]
    }
    assert FuncaoProfissional.objects.filter(pk=funcao_alheia.pk).exists()
    assert not FuncaoProfissional.objects.filter(
        profissional=profissional
    ).exists()


def test_funcao_service_remove_funcoes_por_profissional(
    cargo_profissional,
    usuario_ativo,
):
    """Remove os documentos e exclui logicamente cada função."""
    profissional = criar_profissional()
    outro_cargo = Cargo.objects.create(nome="Encanador")
    funcoes = [
        FuncaoProfissional.objects.create(
            profissional=profissional, cargo=cargo
        )
        for cargo in (cargo_profissional, outro_cargo)
    ]
    documentos = [
        criar_documento(funcao, f"documento-{indice}.pdf")
        for indice, funcao in enumerate(funcoes)
    ]
    FuncaoProfissionalService().remover_por_profissional(
        profissional.id, usuario_ativo
    )

    assert not FuncaoProfissional.objects.filter(
        pk__in=[funcao.pk for funcao in funcoes]
    ).exists()
    assert not DocumentoFuncaoProfissional.objects.filter(
        pk__in=[documento.pk for documento in documentos]
    ).exists()
    assert (
        FuncaoProfissional.dm_objects.filter(
            pk__in=[funcao.pk for funcao in funcoes],
            deletado_por=usuario_ativo,
        ).count()
        == 2
    )


def test_profissional_service_cria_agregado(
    cargo_profissional,
    usuario_ativo,
):
    """Cria o profissional e sincroniza suas funções."""
    arquivo = SimpleUploadedFile(
        "certificado.pdf", b"conteudo", content_type="application/pdf"
    )
    resultado = ProfissionalService().criar(
        {
            "nome": "José",
            "cpf": "12345678901",
            "rg": "123456789",
            "funcoes": [
                {
                    "cargo": cargo_profissional,
                    "documentos": [{"arquivo": arquivo}],
                }
            ],
        },
        usuario_ativo,
    )

    profissional = Profissional.objects.get(pk=resultado["id"])
    funcao = FuncaoProfissional.objects.get(profissional=profissional)
    assert profissional.criado_por == usuario_ativo
    assert resultado["funcoes"][0]["id"] == funcao.id
    assert funcao.cargo == cargo_profissional
    assert funcao.criado_por == usuario_ativo


def test_profissional_service_atualiza_agregado(
    cargo_profissional,
    usuario_ativo,
):
    """Atualiza o profissional e sincroniza suas funções."""
    profissional = criar_profissional()
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    documento = criar_documento(funcao, "certificado.pdf")

    resultado = ProfissionalService().atualizar(
        profissional,
        {
            "nome": "Nome atualizado",
            "funcoes": [
                {
                    "uuid": str(funcao.uuid),
                    "cargo": cargo_profissional,
                    "documentos": [{"uuid": str(documento.uuid)}],
                }
            ],
        },
        usuario_ativo,
    )

    profissional.refresh_from_db()
    funcao.refresh_from_db()
    assert resultado["nome"] == "Nome atualizado"
    assert resultado["funcoes"][0]["id"] == funcao.id
    assert profissional.nome == "Nome atualizado"
    assert profissional.atualizado_por == usuario_ativo
    assert funcao.atualizado_por == usuario_ativo


def test_profissional_service_deleta_agregado(
    cargo_profissional,
    usuario_ativo,
):
    """Remove funções e documentos antes de excluir o profissional."""
    profissional = criar_profissional()
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    documento = criar_documento(funcao, "documento.pdf")

    ProfissionalService().deletar(profissional, usuario_ativo)

    assert not Profissional.objects.filter(pk=profissional.pk).exists()
    assert not FuncaoProfissional.objects.filter(pk=funcao.pk).exists()
    assert not DocumentoFuncaoProfissional.objects.filter(
        pk=documento.pk
    ).exists()
    profissional_excluido = Profissional.dm_objects.get(pk=profissional.pk)
    assert profissional_excluido.deletado_por == usuario_ativo
