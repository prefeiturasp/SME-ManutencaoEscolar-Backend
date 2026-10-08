"""Testes da API de equipes."""

import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.test import APIClient, APIRequestFactory

from apps.empresa.models import Empresa
from apps.equipe.api.views import EquipeViewSet
from apps.equipe.models import Equipe
from apps.lote.models import Lote
from apps.profissional.models import Profissional

pytestmark = pytest.mark.django_db


def test_view_rejeita_usuario_nao_identificado():
    """Rejeita usuário que não corresponde ao modelo da aplicação."""
    view = EquipeViewSet()
    requisicao = APIRequestFactory().post("/api/v1/equipes/")
    requisicao.user = AnonymousUser()
    view.request = requisicao

    with pytest.raises(NotAuthenticated, match="Usuário não identificado"):
        view._obter_usuario()


def test_cria_equipe_com_profissional(
    api_cliente, equipe_payload, usuario_ativo, funcao_profissional
):
    """Cria equipe e vínculo em uma mesma operação."""
    resposta = api_cliente.post(
        "/api/v1/equipes/", equipe_payload, format="json"
    )

    assert resposta.status_code == status.HTTP_201_CREATED, resposta.json()
    equipe = Equipe.objects.get(nome="Equipe Elétrica")
    assert equipe.criado_por == usuario_ativo
    assert equipe.profissionais.count() == 1
    assert equipe.profissionais.get().criado_por == usuario_ativo
    assert equipe.profissionais.get().funcao == funcao_profissional
    assert resposta.json()["profissionais"][0]["funcao"] == str(
        funcao_profissional.uuid
    )


def test_lista_equipes_com_filtro_por_situacao(
    api_cliente: APIClient,
    equipe_existente_ativa: Equipe,
    empresa: Empresa,
    lote_centro: Lote,
) -> None:
    """Lista somente equipes que correspondem aos filtros informados."""
    Equipe.objects.create(
        nome="Equipe inativa",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )

    resposta = api_cliente.get("/api/v1/equipes/", {"situacao": "true"})

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["count"] == 1
    assert resposta.json()["results"] == [
        {
            "nome": equipe_existente_ativa.nome,
            "nome_empresa": empresa.nome,
            "lote": {
                "nome": lote_centro.nome,
                "periodo_inicial": None,
                "periodo_final": None,
            },
            "situacao": True,
        }
    ]


def test_requisicao_sem_autenticacao_retorna_401(equipe_payload):
    """Protege o cadastro contra acesso não autenticado."""
    resposta = APIClient().post(
        "/api/v1/equipes/", equipe_payload, format="json"
    )

    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED


def test_rejeita_equipe_com_nome_repetido(
    api_cliente: APIClient,
    equipe_payload: dict[str, object],
    empresa: Empresa,
    lote_centro: Lote,
) -> None:
    """Converte o erro de nome repetido em resposta de validação."""
    Equipe.objects.create(
        nome="equipe elétrica",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )

    resposta = api_cliente.post(
        "/api/v1/equipes/", equipe_payload, format="json"
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json() == {
        "title": "Já existe uma equipe com este nome!",
        "detail": (
            "Já existe uma equipe com o nome Equipe Elétrica cadastrada na "
            f"empresa {empresa.nome}. Para cadastrar uma nova equipe, "
            "informe um nome diferente."
        ),
    }


def test_rejeita_profissional_inativo(
    api_cliente: APIClient,
    equipe_payload: dict[str, object],
    profissional_ativo: Profissional,
) -> None:
    """Converte o erro do Django para uma resposta de validação."""
    profissional_ativo.status = False
    profissional_ativo.save(update_fields=["status"])

    resposta = api_cliente.post(
        "/api/v1/equipes/", equipe_payload, format="json"
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json() == {
        "profissionais": [
            "Não é permitido vincular um profissional inativo à equipe."
        ]
    }


def test_rejeita_profissional_vinculado_a_outra_equipe(
    api_cliente: APIClient,
    equipe_payload: dict[str, object],
    erro_profissional_vinculado: dict[str, str],
) -> None:
    """Retorna erro singular para profissional já vinculado."""
    resposta = api_cliente.post(
        "/api/v1/equipes/", equipe_payload, format="json"
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json() == erro_profissional_vinculado


def test_rejeita_varios_profissionais_vinculados(
    api_cliente: APIClient,
    equipe_payload: dict[str, object],
    erro_varios_profissionais_vinculados: dict[str, object],
) -> None:
    """Retorna erro plural quando vários profissionais estão vinculados."""
    resposta = api_cliente.post(
        "/api/v1/equipes/", equipe_payload, format="json"
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json() == erro_varios_profissionais_vinculados
