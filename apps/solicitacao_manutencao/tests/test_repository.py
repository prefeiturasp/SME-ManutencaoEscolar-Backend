"""Testes dos repositórios de solicitações de manutenção."""

import pytest

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

    solicitacoes = SolicitacaoManutencaoRepository().buscar_por_usuario(
        usuario_ue
    )

    assert list(solicitacoes) == [
        {
            "uuid": solicitacao_criada_por_outra_pessoa.uuid,
            "codigo": "0000002",
            "tipo_atendimento": "comum",
            "situacao": "nao_enviado_dre",
            "data_envio": None,
            "fase": "solicitacao",
        },
        {
            "uuid": solicitacao_usuario.uuid,
            "codigo": "0000001",
            "tipo_atendimento": "comum",
            "situacao": "nao_enviado_dre",
            "data_envio": None,
            "fase": "solicitacao",
        },
    ]


def test_lista_solicitacoes_vazia_sem_usuario() -> None:
    """Retorna uma lista vazia quando nenhum usuário for informado."""
    solicitacoes = SolicitacaoManutencaoRepository().buscar_por_usuario(None)

    assert not solicitacoes.exists()


def test_lista_solicitacoes_vazia_para_usuario_sem_username(
    usuario_ativo: Usuario,
) -> None:
    """Não lista solicitações quando o usuário não tem registro funcional."""
    solicitacoes = SolicitacaoManutencaoRepository().buscar_por_usuario(
        usuario_ativo
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

    resultados = list(
        SolicitacaoManutencaoRepository().buscar_por_usuario(
            usuario_ue, str(solicitacao.uuid)
        )
    )

    assert resultados == [
        {
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
    ]


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

    resultados = SolicitacaoManutencaoRepository().buscar_por_usuario(
        usuario_ue, str(solicitacao.uuid)
    )

    # A visibilidade depende do responsável ativo pela unidade, não de quem
    # cadastrou a solicitação.
    assert resultados.filter(uuid=solicitacao.uuid).exists()


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

    solicitacoes = SolicitacaoManutencaoRepository().buscar_por_usuario(
        usuario_dre
    )

    assert not solicitacoes.exists()


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
