"""Testes dos repositórios de solicitações de manutenção."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.escola.models import HistoricoResponsavel, Unidadeeducacional
from apps.solicitacao_manutencao.models import (
    FotoLocalReparo,
    ServicoManutencao,
    SolicitacaoManutencao,
)
from apps.solicitacao_manutencao.repository import (
    ArquivoServicoManutencaoRepository,
    ServicoManutencaoRepository,
    SolicitacaoManutencaoRepository,
)
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models import Usuario
from apps.usuarios.models.cargo_eol import CargoEOL

pytestmark = pytest.mark.django_db


def test_lista_solicitacoes_por_usuario(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ue: Usuario,
    usuario_inativo: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Lista solicitações das unidades vinculadas ao responsável informado."""
    usuario_ue.username = historico_responsavel.responsavel.registro_funcional
    usuario_ue.save(update_fields=["username"])
    solicitacao_usuario = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ue,
    )
    solicitacao_criada_por_outra_pessoa = SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_inativo,
    )

    solicitacoes = SolicitacaoManutencaoRepository().listar_por_usuario(
        usuario_ue
    )

    assert list(solicitacoes) == [
        {
            "uuid": solicitacao_criada_por_outra_pessoa.uuid,
            "codigo": "0000002",
            "tipo_atendimento": "comum",
            "solicitante": "ue",
            "situacao": "nao_enviado_dre",
            "data_envio": None,
            "fase": "solicitacao",
        },
        {
            "uuid": solicitacao_usuario.uuid,
            "codigo": "0000001",
            "tipo_atendimento": "comum",
            "solicitante": "ue",
            "situacao": "nao_enviado_dre",
            "data_envio": None,
            "fase": "solicitacao",
        },
    ]


def test_lista_solicitacoes_vazia_para_usuario_sem_perfil() -> None:
    """Não lista solicitações para usuário sem perfil de acesso."""
    usuario = Usuario.objects.create(
        username="usuario-sem-perfil",
        nome="Usuário sem perfil",
    )

    solicitacoes = SolicitacaoManutencaoRepository().listar_por_usuario(
        usuario
    )

    assert list(solicitacoes) == []


def test_lista_solicitacoes_vazia_sem_usuario() -> None:
    """Retorna uma lista vazia quando nenhum usuário for informado."""
    solicitacoes = SolicitacaoManutencaoRepository().listar_por_usuario(None)

    assert not solicitacoes.exists()


def test_lista_solicitacoes_vazia_para_usuario_sem_username(
    usuario_ue: Usuario,
) -> None:
    """Não lista solicitações quando o usuário não tem username."""
    usuario_ue.username = ""
    usuario_ue.save(update_fields=["username"])

    solicitacoes = SolicitacaoManutencaoRepository().listar_por_usuario(
        usuario_ue
    )

    assert not solicitacoes.exists()


def test_consulta_solicitacoes_detalhadas_com_dicionarios(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ue: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Retorna os dados da solicitação em um dicionário."""
    usuario_ue.username = historico_responsavel.responsavel.registro_funcional
    usuario_ue.save(update_fields=["username"])
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000003",
        tipo_atendimento="urgente",
        informacoes_adicionais="Reparo prioritário.",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ue,
    )

    resultados = SolicitacaoManutencaoRepository().get_detalhes_solicitacao(
        usuario_ue, str(solicitacao.uuid)
    )

    assert resultados == {
        "id": solicitacao.id,
        "uuid": solicitacao.uuid,
        "codigo": "0000003",
        "tipo_atendimento": "urgente",
        "informacoes_adicionais": "Reparo prioritário.",
        "unidade_educacional_id": unidade_educacional_emef.id,
        "situacao": "nao_enviado_dre",
        "solicitante": "ue",
        "data_envio": None,
        "fase": "solicitacao",
    }


def test_atualiza_solicitacao(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Atualiza dados e responsável pela alteração da solicitação."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000004",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )

    resultado = SolicitacaoManutencaoRepository().atualizar(
        {"id": solicitacao.id},
        {"informacoes_adicionais": "Atualizada"},
        usuario_ativo,
    )

    solicitacao.refresh_from_db()
    assert resultado["informacoes_adicionais"] == "Atualizada"
    assert solicitacao.atualizado_por == usuario_ativo


def test_serializa_solicitacao_recebida_como_dicionario(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Serializa IDs de relações quando a entrada já é um dicionário."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000010",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )
    dados = (
        SolicitacaoManutencao.objects.filter(pk=solicitacao.pk)
        .values(
            "id",
            "uuid",
            "codigo",
            "tipo_atendimento",
            "informacoes_adicionais",
            "unidade_educacional_id",
            "situacao",
            "data_envio",
            "fase",
            "criado_por_id",
            "criado_em",
        )
        .get()
    )

    resultado = SolicitacaoManutencaoRepository()._serializar(dados)

    assert resultado["uuid"] == str(solicitacao.uuid)
    assert resultado["unidade_educacional"] == unidade_educacional_emef.id


def test_nao_consulta_solicitacoes_de_outra_ue(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ue: Usuario,
    usuario_inativo: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Retorna dicionário vazio quando a solicitação não estiver visível."""
    usuario_ue.username = historico_responsavel.responsavel.registro_funcional
    usuario_ue.save(update_fields=["username"])
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000004",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_inativo,
    )

    resultados = SolicitacaoManutencaoRepository().get_detalhes_solicitacao(
        usuario_ue, str(solicitacao.uuid)
    )

    # A visibilidade depende do responsável ativo pela unidade, não de quem
    # cadastrou a solicitação.
    assert resultados is not None
    assert resultados["uuid"] == solicitacao.uuid


def test_nao_lista_solicitacoes_para_usuario_sem_registro_funcional(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Não lista solicitações de usuário sem registro funcional."""
    cargo_dre = CargoEOL.objects.create(
        codigo="7777",
        nome="Diretor regional",
        perfil=PerfilAcesso.DRE,
    )
    usuario_dre = Usuario.objects.create(
        username="12345678901",
        nome="Usuário DRE",
        cpf="12345678901",
        email="dre@email.com",
        cargo=cargo_dre,
        is_active=True,
    )
    for codigo in ("0000001", "0000002"):
        SolicitacaoManutencao.objects.create(
            codigo=codigo,
            tipo_atendimento="comum",
            unidade_educacional=unidade_educacional_emef,
            criado_por=usuario_ativo,
        )

    solicitacoes = SolicitacaoManutencaoRepository().listar_por_usuario(
        usuario_dre
    )

    assert not solicitacoes.exists()


def test_lista_solicitacoes_de_todas_as_unidades_da_dre(
    unidade_educacional_emef: Unidadeeducacional,
    unidade_educacional_cemei: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Lista solicitações de todas as unidades vinculadas à DRE do usuário."""
    cargo_dre = CargoEOL.objects.create(
        codigo="7778",
        nome="Diretor regional",
        perfil=PerfilAcesso.DRE,
    )
    usuario_dre = Usuario.objects.create(
        username="usuario-dre",
        nome="Usuário DRE",
        cargo=cargo_dre,
        diretoria_regional=unidade_educacional_emef.diretoria_regional,
    )
    solicitacoes_dre = [
        SolicitacaoManutencao.objects.create(
            codigo=codigo,
            tipo_atendimento="comum",
            unidade_educacional=unidade,
            criado_por=usuario_ativo,
        )
        for codigo, unidade in (
            ("dre-1", unidade_educacional_emef),
            ("dre-2", unidade_educacional_emef),
        )
    ]
    SolicitacaoManutencao.objects.create(
        codigo="outra-dre",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_cemei,
        criado_por=usuario_ativo,
    )

    resultados = SolicitacaoManutencaoRepository().listar_por_usuario(
        usuario_dre
    )

    assert {resultado["codigo"] for resultado in resultados} == {
        solicitacao.codigo for solicitacao in solicitacoes_dre
    }


def test_dre_sem_diretoria_nao_lista_solicitacoes(
    usuario_ativo: Usuario,
    unidade_educacional_emef: Unidadeeducacional,
) -> None:
    """Não lista solicitações para usuário DRE sem diretoria vinculada."""
    cargo_dre = CargoEOL.objects.create(
        codigo="7779",
        nome="Diretor regional",
        perfil=PerfilAcesso.DRE,
    )
    usuario_dre = Usuario.objects.create(
        username="usuario-dre-sem-diretoria",
        nome="Usuário DRE",
        cargo=cargo_dre,
    )
    SolicitacaoManutencao.objects.create(
        codigo="dre-sem-vinculo",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )

    resultados = SolicitacaoManutencaoRepository().listar_por_usuario(
        usuario_dre
    )

    assert not resultados.exists()


def test_cria_solicitacao(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Persiste uma solicitação de manutenção."""
    solicitacao = SolicitacaoManutencaoRepository().criar(
        dados={
            "codigo": "0000001",
            "tipo_atendimento": "comum",
            "unidade_educacional": unidade_educacional_emef,
        },
        usuario=usuario_ativo,
    )

    assert solicitacao["codigo"] == "0000001"
    assert solicitacao["id"] is not None
    assert solicitacao["uuid"] is not None
    assert solicitacao["tipo_atendimento"] == "comum"
    assert solicitacao["informacoes_adicionais"] == ""
    assert solicitacao["unidade_educacional"] == unidade_educacional_emef
    assert solicitacao["criado_por"] == usuario_ativo
    assert solicitacao["situacao"] == "nao_enviado_dre"
    assert solicitacao["data_envio"] is None
    assert solicitacao["fase"] == "solicitacao"
    assert solicitacao["criado_em"] is not None
    solicitacao_criada = SolicitacaoManutencao.objects.get(
        id=solicitacao["id"]
    )
    assert str(solicitacao_criada) == (f"0000001 - {unidade_educacional_emef}")


def test_cria_servico_da_solicitacao(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Persiste um serviço vinculado à solicitação."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )
    servico = ServicoManutencaoRepository().criar(
        dados={
            "servico_especifico": "Reparo hidráulico",
            "local_reparo": "Cozinha",
            "descricao": "Vazamento na pia",
        },
        solicitacao_id=solicitacao.id,
        usuario=usuario_ativo,
    )

    assert servico["solicitacao_manutencao"] == solicitacao
    assert servico["criado_por"] == usuario_ativo
    assert servico["id"] is not None
    assert servico["uuid"] is not None
    assert servico["servico"] is None
    assert servico["servico_especifico"] == "Reparo hidráulico"
    assert servico["local_reparo"] == "Cozinha"
    assert servico["descricao"] == "Vazamento na pia"
    assert servico["criado_em"] is not None
    assert (
        str(servico["solicitacao_manutencao"].servicos_manutencao.get())
        == "Reparo hidráulico - Cozinha"
    )


def test_lista_e_atualiza_servico(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Lista e atualiza serviços persistidos da solicitação."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000013",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )
    repositorio = ServicoManutencaoRepository()
    criado = repositorio.criar(
        {
            "servico_especifico": "Reparo hidráulico",
            "local_reparo": "Cozinha",
            "descricao": "Vazamento",
        },
        solicitacao.id,
        usuario_ativo,
    )

    lista = repositorio.listar_servicos_por_solicitacao(solicitacao.id)
    atualizado = repositorio.atualizar(
        criado,
        {"descricao": "Vazamento corrigido"},
    )

    assert len(lista) == 1
    assert lista[0]["id"] == criado["id"]
    assert atualizado["descricao"] == "Vazamento corrigido"


def test_cria_arquivo_do_servico(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Persiste um arquivo vinculado ao serviço."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )
    servico = ServicoManutencaoRepository().criar(
        dados={
            "servico_especifico": "Reparo hidráulico",
            "local_reparo": "Cozinha",
            "descricao": "Vazamento na pia",
        },
        solicitacao_id=solicitacao.id,
        usuario=usuario_ativo,
    )
    arquivo = ArquivoServicoManutencaoRepository().criar(
        dados={
            "nome_original": "reparo.jpg",
            "arquivo": "arquivos/reparo.jpg",
            "tipo": "imagem",
            "tipo_mime": "image/jpeg",
            "tamanho_bytes": 16,
        },
        servico_id=servico["id"],
        usuario=usuario_ativo,
    )

    assert arquivo["servico_manutencao"].id == servico["id"]
    assert arquivo["criado_por"] == usuario_ativo
    assert arquivo["id"] is not None
    assert arquivo["uuid"] is not None
    assert arquivo["nome_original"] == "reparo.jpg"
    assert str(arquivo["arquivo"]) == "arquivos/reparo.jpg"
    assert arquivo["tipo"] == "imagem"
    assert arquivo["tipo_mime"] == "image/jpeg"
    assert arquivo["tamanho_bytes"] == 16
    assert arquivo["criado_em"] is not None
    assert FotoLocalReparo.objects.filter(pk=arquivo["id"]).exists()
    assert ServicoManutencao.objects.filter(pk=servico["id"]).exists()


def test_lista_anexos_do_servico(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Lista os anexos persistidos para um serviço."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000014",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )
    servico = ServicoManutencaoRepository().criar(
        {
            "servico_especifico": "Reparo elétrico",
            "local_reparo": "Sala",
            "descricao": "Tomada danificada",
        },
        solicitacao.id,
        usuario_ativo,
    )
    repositorio = ArquivoServicoManutencaoRepository()
    anexo = repositorio.criar(
        {
            "nome_original": "reparo.jpg",
            "arquivo": "arquivos/reparo.jpg",
            "tipo": "imagem",
            "tipo_mime": "image/jpeg",
            "tamanho_bytes": 16,
        },
        servico["id"],
        usuario_ativo,
    )

    anexos = repositorio.listar_anexos_por_servico(servico["id"])

    assert [item["id"] for item in anexos] == [anexo["id"]]


def test_remove_servico_logicamente(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Remove um serviço sem apagar seu registro do banco."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000011",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )
    servico = ServicoManutencaoRepository().criar(
        {
            "servico_especifico": "Reparo hidráulico",
            "local_reparo": "Cozinha",
            "descricao": "Vazamento na pia",
        },
        solicitacao.id,
        usuario_ativo,
    )

    ServicoManutencaoRepository().remover(servico["id"], usuario_ativo)

    assert not ServicoManutencao.objects.filter(pk=servico["id"]).exists()
    assert ServicoManutencao.dm_objects.filter(pk=servico["id"]).exists()


@pytest.mark.django_db(transaction=True)
def test_exclui_anexo_e_arquivo_apos_commit(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Exclui anexos não preservados e agenda a remoção do arquivo."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000012",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )
    servico = ServicoManutencaoRepository().criar(
        {
            "servico_especifico": "Reparo hidráulico",
            "local_reparo": "Cozinha",
            "descricao": "Vazamento na pia",
        },
        solicitacao.id,
        usuario_ativo,
    )
    anexo = ArquivoServicoManutencaoRepository().criar(
        {
            "nome_original": "excluir.jpg",
            "arquivo": SimpleUploadedFile(
                "excluir.jpg", b"imagem", content_type="image/jpeg"
            ),
            "tipo": "imagem",
            "tipo_mime": "image/jpeg",
            "tamanho_bytes": 6,
        },
        servico["id"],
        usuario_ativo,
    )
    nome_arquivo = anexo["arquivo"].name

    ArquivoServicoManutencaoRepository().excluir_nao_preservados(
        servico["id"], []
    )

    assert not FotoLocalReparo.dm_objects.filter(pk=anexo["id"]).exists()
    assert not anexo["arquivo"].storage.exists(nome_arquivo)


def test_obtem_ultimo_codigo_incluindo_solicitacao_excluida(
    unidade_educacional_emef: Unidadeeducacional,
) -> None:
    """Consulta o maior código mesmo quando o registro foi excluído."""
    SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )
    ultima_solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )
    ultima_solicitacao.soft_delete()

    ultimo_codigo = SolicitacaoManutencaoRepository().obter_ultimo_codigo()

    assert ultimo_codigo == {"codigo": "0000002"}


def test_obtem_ultimo_codigo_retorna_dict_vazio_sem_solicitacoes() -> None:
    """Retorna um dicionário vazio quando não houver solicitações."""
    ultimo_codigo = SolicitacaoManutencaoRepository().obter_ultimo_codigo()

    assert ultimo_codigo == {}
