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
    """Deve retornar o payload recebido do service."""
    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.autentica",
        classmethod(lambda cls, login, senha: {"token": "abc"}),
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
    assert response.data == {"token": "abc"}
