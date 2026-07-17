from django.urls import resolve, reverse


def test_core_urls_resolve_health_and_login_routes():
    """Verifica se as URLs estão configuradas corretamente."""
    assert reverse("health-check") == "/api/v1/health/"
    assert reverse("login") == "/api/v1/login/"

    assert resolve("/api/v1/health/").view_name == "health-check"
    assert resolve("/api/v1/login/").view_name == "login"
