from uuid import UUID

import pytest

from apps.core.api.views import HealthCheckView, LoginView


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
