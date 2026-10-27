"""Testes dos serviços do domínio Equipe."""

from typing import Any

import pytest
from django.core.exceptions import ValidationError

from apps.cargo.models import Cargo
from apps.empresa.models import Empresa
from apps.equipe.exceptions import (
    EquipeJaCadastradaError,
    ProfissionaisVinculadosError,
    ProfissionalVinculadoError,
)
from apps.equipe.models import Equipe, ProfissionalEquipe
from apps.equipe.serializers import EquipeCriarEditarSerializer
from apps.equipe.services import EquipeService
from apps.lote.models import Lote
from apps.profissional.models import FuncaoProfissional, Profissional
from apps.usuarios.models import Usuario

pytestmark = pytest.mark.django_db


def _validar_payload(equipe_payload: dict[str, object]) -> dict[str, Any]:
    """Converta o payload da API nos dados esperados pelo serviço."""
    serializer = EquipeCriarEditarSerializer(data=equipe_payload)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def test_cria_equipe_com_profissional(
    equipe_payload: dict[str, object], usuario_ativo
) -> None:
    """Cria a equipe e seu vínculo em uma mesma operação."""
    equipe = EquipeService().criar(
        _validar_payload(equipe_payload), usuario_ativo
    )

    equipe_criada = Equipe.objects.get(uuid=equipe["uuid"])
    assert equipe_criada.criado_por == usuario_ativo
    assert equipe_criada.profissionais.count() == 1
    assert equipe_criada.profissionais.get().criado_por == usuario_ativo


def test_rejeita_profissional_inativo(
    equipe_payload: dict[str, object], profissional_ativo, usuario_ativo
) -> None:
    """Não permite vincular profissional inativo."""
    profissional_ativo.status = False
    profissional_ativo.save(update_fields=["status"])
    dados_validados = _validar_payload(equipe_payload)
    service = EquipeService()

    with pytest.raises(ValidationError, match="profissional inativo"):
        service.criar(dados_validados, usuario_ativo)

    assert not Equipe.objects.exists()


def test_rejeita_profissional_de_outra_equipe_ativa(
    equipe_payload: dict[str, object],
    erro_profissional_vinculado: dict[str, str],
    usuario_ativo,
) -> None:
    """Não permite profissional que já pertence a equipe ativa."""
    dados_validados = _validar_payload(equipe_payload)
    service = EquipeService()

    with pytest.raises(ProfissionalVinculadoError) as exc_info:
        service.criar(dados_validados, usuario_ativo)

    assert exc_info.value.title == erro_profissional_vinculado["title"]
    assert exc_info.value.detail == erro_profissional_vinculado["detail"]


def test_rejeita_varios_profissionais_vinculados_a_equipes_ativas(
    equipe_payload: dict[str, object],
    erro_varios_profissionais_vinculados: dict[str, object],
    usuario_ativo,
) -> None:
    """Retorna mensagem plural quando vários profissionais têm vínculo."""
    dados_validados = _validar_payload(equipe_payload)
    service = EquipeService()

    with pytest.raises(ProfissionaisVinculadosError) as exc_info:
        service.criar(dados_validados, usuario_ativo)

    assert (
        exc_info.value.title == erro_varios_profissionais_vinculados["title"]
    )
    assert (
        exc_info.value.detail == erro_varios_profissionais_vinculados["detail"]
    )


def test_permite_profissional_de_outra_equipe_inativa(
    equipe_payload: dict[str, object],
    empresa,
    lote_centro,
    profissional_ativo,
    funcao_profissional,
    usuario_ativo,
) -> None:
    """Permite reutilizar profissional cujo vínculo anterior é inativo."""
    equipe_existente = Equipe.objects.create(
        nome="Equipe Existente",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )
    ProfissionalEquipe.objects.create(
        equipe=equipe_existente,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )

    equipe = EquipeService().criar(
        _validar_payload(equipe_payload), usuario_ativo
    )

    assert Equipe.objects.get(uuid=equipe["uuid"]).profissionais.count() == 1


def test_rejeita_nome_repetido_na_mesma_empresa(
    equipe_payload: dict[str, object],
    empresa,
    lote_centro,
    usuario_ativo,
) -> None:
    """Não permite nome repetido dentro da mesma empresa."""
    Equipe.objects.create(
        nome="equipe elétrica",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )
    dados_validados = _validar_payload(equipe_payload)
    service = EquipeService()

    with pytest.raises(EquipeJaCadastradaError) as exc_info:
        service.criar(dados_validados, usuario_ativo)

    assert exc_info.value.title == "Já existe uma equipe com este nome!"
    assert exc_info.value.detail == (
        "Já existe uma equipe com o nome Equipe Elétrica cadastrada na "
        f"empresa {empresa.nome}. Para cadastrar uma nova equipe, "
        "informe um nome diferente."
    )


def test_atualiza_equipe_e_sincroniza_profissionais(
    equipe_payload: dict[str, object],
    usuario_ativo,
    funcao_profissional: FuncaoProfissional,
) -> None:
    """Atualiza vínculos mantidos, adicionados e removidos da equipe."""
    service = EquipeService()
    resultado_criacao = service.criar(
        _validar_payload(equipe_payload), usuario_ativo
    )
    equipe = Equipe.objects.get(uuid=resultado_criacao["uuid"])
    vinculo_removido = equipe.profissionais.get()
    novo_profissional = Profissional.objects.create(
        nome="Maria Encanadora",
        cpf="98765432101",
        rg="987654321",
        status=True,
    )
    nova_funcao = FuncaoProfissional.objects.create(
        profissional=novo_profissional,
        cargo=funcao_profissional.cargo,
    )
    payload_atualizado = {
        **equipe_payload,
        "nome": "Equipe Hidráulica",
        "profissionais": [
            {
                "profissional": str(novo_profissional.uuid),
                "funcao": str(nova_funcao.uuid),
            }
        ],
    }

    equipe_atualizada = service.atualizar(
        equipe, _validar_payload(payload_atualizado), usuario_ativo
    )

    equipe.refresh_from_db()
    assert equipe_atualizada["nome"] == "Equipe Hidráulica"
    assert equipe.atualizado_por == usuario_ativo
    novo_vinculo = equipe.profissionais.get()
    assert novo_vinculo.profissional == novo_profissional
    vinculo_ativo = ProfissionalEquipe.objects.filter(pk=vinculo_removido.pk)
    assert not vinculo_ativo.exists()
    vinculo_excluido = ProfissionalEquipe.dm_objects.get(
        pk=vinculo_removido.pk
    )
    assert vinculo_excluido.deletado_por == usuario_ativo


def test_atualiza_funcao_do_profissional_na_equipe(
    equipe_payload: dict[str, object],
    usuario_ativo,
    profissional_ativo: Profissional,
    funcao_profissional: FuncaoProfissional,
) -> None:
    """Atualiza o vínculo existente sem criar um novo registro."""
    service = EquipeService()
    resultado_criacao = service.criar(
        _validar_payload(equipe_payload), usuario_ativo
    )
    equipe = Equipe.objects.get(uuid=resultado_criacao["uuid"])
    vinculo = equipe.profissionais.get()
    nova_funcao = FuncaoProfissional.objects.create(
        profissional=profissional_ativo,
        cargo=Cargo.objects.create(nome="Supervisor"),
    )
    payload_atualizado = {
        **equipe_payload,
        "profissionais": [
            {
                "profissional": str(profissional_ativo.uuid),
                "funcao": str(nova_funcao.uuid),
            }
        ],
    }

    service.atualizar(
        equipe, _validar_payload(payload_atualizado), usuario_ativo
    )

    vinculo.refresh_from_db()
    assert vinculo.funcao == nova_funcao
    assert vinculo.atualizado_por == usuario_ativo
    assert equipe.profissionais.count() == 1


def test_nao_atualiza_vinculo_do_profissional_sem_alteracoes(
    equipe_payload: dict[str, object],
    empresa,
    lote_centro,
    profissional_ativo: Profissional,
    funcao_profissional: FuncaoProfissional,
    usuario_ativo,
) -> None:
    """Mantém a auditoria do vínculo quando a função não foi alterada."""
    service = EquipeService()
    dados_validados = _validar_payload(equipe_payload)
    equipe = Equipe.objects.create(
        nome="Equipe Elétrica",
        situacao=True,
        empresa=empresa,
        lote=lote_centro,
    )
    vinculo = ProfissionalEquipe.objects.create(
        equipe=equipe,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )
    atualizado_em = vinculo.atualizado_em

    service.atualizar(equipe, dados_validados, usuario_ativo)

    vinculo.refresh_from_db()
    assert vinculo.atualizado_por is None
    assert vinculo.atualizado_em == atualizado_em


def test_rejeita_ativacao_com_profissional_em_outra_equipe_ativa(
    empresa: Empresa,
    lote_centro: Lote,
    profissional_vinculado: ProfissionalEquipe,
    funcao_profissional: FuncaoProfissional,
    usuario_ativo: Usuario,
) -> None:
    """Não ativa equipe com profissional vinculado a outra equipe ativa."""
    equipe = Equipe.objects.create(
        nome="Equipe Inativa",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )
    ProfissionalEquipe.objects.create(
        equipe=equipe,
        profissional=profissional_vinculado.profissional,
        funcao=funcao_profissional,
    )
    service = EquipeService()

    with pytest.raises(ProfissionalVinculadoError):
        service.atualizar(
            equipe,
            {"situacao": True},
            usuario_ativo,
        )

    equipe.refresh_from_db()
    assert equipe.situacao is False
