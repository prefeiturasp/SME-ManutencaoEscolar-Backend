from uuid import UUID

import pytest

from apps.core.api.views import HealthCheckView, LoginView
from apps.core.exceptions import (
    FalhaAutenticacaoError,
    InternalError,
    SmeIntegracaoError,
)


@pytest.mark.django_db
def test_healthcheck_retorna_ok(api_factory):
    """Deve retornar status da aplicação."""
    request = api_factory.get("/api/v1/health/")

    response = HealthCheckView.as_view()(request)

    assert response.status_code == 200
    assert response.data == {"status": "ok"}


@pytest.mark.django_db
def test_login_retorna_payload_autenticado(api_factory, monkeypatch):
    """Deve retornar o payload autenticado."""
    dados = {
        "refresh": "refresh-token",
        "access": "access-token",
        "usuario": {
            "id": 1,
            "uuid": UUID("2e7d7d7d-9b8b-4c92-9b3b-123456789abc"),
            "nome": "João da Silva",
            "email": "joao.silva@sme.prefeitura.sp.gov.br",
            "registro_funcional": "1234567",
            "cpf": "12345678901",
            "username": "1234567",
            "perfil_acesso": {
                "cargo": "DIRETOR DE ESCOLA",
                "perfil": {
                    "codigo": "UE",
                    "descricao": "Diretor Unidade Educacional",
                },
            },
        },
    }
    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.login",
        classmethod(lambda cls, login, senha: dados),
    )

    request = api_factory.post(
        "/login/",
        {
            "login": "1234567",
            "senha": "senha123",
        },
        format="json",
    )

    response = LoginView.as_view()(request)

    assert response.status_code == 200
    print(response.data)
    assert response.data == dados


@pytest.mark.django_db
def test_login_retorna_401_quando_credenciais_invalidas(
    api_factory, monkeypatch
):
    """Deve retornar 401 quando as credenciais forem inválidas."""

    def mock_login_401(cls, login, senha):
        raise FalhaAutenticacaoError()

    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.login",
        classmethod(mock_login_401),
    )

    request = api_factory.post(
        "/login/",
        {
            "login": "1234567",
            "senha": "senha_invalida",
        },
        format="json",
    )

    response = LoginView.as_view()(request)

    assert response.status_code == 401
    assert response.data["detail"] == "Usuário e/ou senha inválida"


@pytest.mark.django_db
def test_login_retorna_503_quando_eol_esta_indisponivel(
    api_factory, monkeypatch
):
    """Deve retornar 503 quando ocorrer falha de integração."""

    def mock_login_503(cls, login, senha):
        raise SmeIntegracaoError()

    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.login",
        classmethod(mock_login_503),
    )

    request = api_factory.post(
        "/login/",
        {
            "login": "1234567",
            "senha": "senha123",
        },
        format="json",
    )

    response = LoginView.as_view()(request)

    assert response.status_code == 503
    assert response.data == {
        "detail": (
            "Parece que estamos com uma instabilidade no momento. "
            "Tente entrar novamente daqui a pouco."
        )
    }


@pytest.mark.django_db
def test_login_retorna_500_quando_ocorre_erro_interno(
    api_factory, monkeypatch
):
    """Deve retornar 500 quando ocorrer erro interno."""

    def mock_login_500(cls, login, senha):
        raise InternalError()

    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.login",
        classmethod(mock_login_500),
    )

    request = api_factory.post(
        "/login/",
        {
            "login": "1234567",
            "senha": "senha123",
        },
        format="json",
    )

    response = LoginView.as_view()(request)

    assert response.status_code == 500
    assert response.data == {
        "detail": (
            "Parece que estamos com uma instabilidade no momento. "
            "Tente entrar novamente daqui a pouco."
        )
    }
