"""Fixtures dos testes do domínio Equipe."""

import pytest

from apps.cargo.models import Cargo
from apps.empresa.models import Empresa
from apps.equipe.constants import EquipeErrorMessages
from apps.equipe.models import Equipe, ProfissionalEquipe
from apps.lote.models import Lote
from apps.profissional.models import FuncaoProfissional, Profissional


@pytest.fixture
def profissional_ativo(db: None) -> Profissional:
    """Cria um profissional ativo."""
    return Profissional.objects.create(
        nome="João Eletricista",
        cpf="12345678901",
        rg="123456789",
        status=True,
    )


@pytest.fixture
def funcao_profissional(
    profissional_ativo: Profissional,
) -> FuncaoProfissional:
    """Cria uma função para o profissional ativo."""
    cargo = Cargo.objects.create(nome="Eletricista")
    return FuncaoProfissional.objects.create(
        profissional=profissional_ativo,
        cargo=cargo,
    )


@pytest.fixture
def equipe_payload(
    empresa,
    lote_centro,
    profissional_ativo: Profissional,
    funcao_profissional: FuncaoProfissional,
) -> dict[str, object]:
    """Retorna um payload válido para criação de equipe."""
    return {
        "nome": "Equipe Elétrica",
        "situacao": True,
        "empresa": str(empresa.uuid),
        "lote": str(lote_centro.uuid),
        "profissionais": [
            {
                "profissional": str(profissional_ativo.uuid),
                "funcao": str(funcao_profissional.uuid),
            }
        ],
    }


@pytest.fixture
def equipe_existente_ativa(empresa: Empresa, lote_centro: Lote) -> Equipe:
    """Cria uma equipe ativa para os cenários de vínculo existente."""
    return Equipe.objects.create(
        nome="Equipe Existente",
        situacao=True,
        empresa=empresa,
        lote=lote_centro,
    )


@pytest.fixture
def profissional_vinculado(
    equipe_existente_ativa: Equipe,
    profissional_ativo: Profissional,
    funcao_profissional: FuncaoProfissional,
) -> ProfissionalEquipe:
    """Vincula o profissional ativo a uma equipe existente."""
    return ProfissionalEquipe.objects.create(
        equipe=equipe_existente_ativa,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )


@pytest.fixture
def erro_profissional_vinculado(
    profissional_vinculado: ProfissionalEquipe,
) -> dict[str, str]:
    """Retorna o erro esperado para um profissional já vinculado."""
    vinculo = profissional_vinculado
    return {
        "title": "Profissional já vinculado a uma equipe!",
        "detail": (
            f"O profissional {vinculo.profissional.nome} já possui vínculo "
            f"com a equipe {vinculo.equipe.nome}. Para incluir esse "
            "registro, primeiro remova o vínculo atual com a equipe."
        ),
    }


@pytest.fixture
def erro_varios_profissionais_vinculados(
    equipe_payload: dict[str, object],
    profissional_vinculado: ProfissionalEquipe,
    funcao_profissional: FuncaoProfissional,
) -> dict[str, object]:
    """Prepara e retorna o erro esperado para dois profissionais vinculados."""
    outro_profissional = Profissional.objects.create(
        nome="Maria Encanadora",
        cpf="98765432101",
        rg="987654321",
        status=True,
    )
    outra_funcao = FuncaoProfissional.objects.create(
        profissional=outro_profissional,
        cargo=funcao_profissional.cargo,
    )
    ProfissionalEquipe.objects.create(
        equipe=profissional_vinculado.equipe,
        profissional=outro_profissional,
        funcao=outra_funcao,
    )
    profissionais = equipe_payload["profissionais"]
    assert isinstance(profissionais, list)
    profissionais.append(
        {
            "profissional": str(outro_profissional.uuid),
            "funcao": str(outra_funcao.uuid),
        }
    )
    equipe = profissional_vinculado.equipe
    return {
        "title": EquipeErrorMessages.PROFISSIONAIS_OUTRA_EQUIPE_TITULO,
        "detail": {
            "message": EquipeErrorMessages.PROFISSIONAIS_OUTRA_EQUIPE,
            "vinculados": [
                {
                    "profissional": outro_profissional.nome,
                    "equipe": equipe.nome,
                },
                {
                    "profissional": profissional_vinculado.profissional.nome,
                    "equipe": equipe.nome,
                },
            ],
        },
    }
