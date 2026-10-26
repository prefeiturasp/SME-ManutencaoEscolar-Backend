import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from apps.usuarios.api.views.usuario_views import UsuarioViewSet
from apps.usuarios.models.usuario import Usuario

pytestmark = pytest.mark.django_db


class TestUsuarioView:
    def test_me_retorna_dados_usuario(
        self, monkeypatch, usuario_ativo_dict, api_factory, usuario_ativo
    ):
        """Deve retornar os dados do usuário autenticado."""
        request = api_factory.get("/usuarios/me/")
        force_authenticate(request, user=usuario_ativo)

        response = UsuarioViewSet.as_view(
            {"get": "me"},
        )(request)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == usuario_ativo_dict["username"]
        assert response.data["nome"] == usuario_ativo_dict["nome"]
        assert response.data["email"] == usuario_ativo_dict["email"]

    def test_me_retorna_funcionalidades_do_perfil(
        self, api_factory, usuario_ativo
    ):
        """Deve retornar as funcionalidades liberadas ao perfil."""
        request = api_factory.get("/usuarios/me/")
        force_authenticate(request, user=usuario_ativo)

        response = UsuarioViewSet.as_view({"get": "me"})(request)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["funcionalidades"] == [
            "CADASTROS",
            "RELATORIOS",
            "SOLICITACAO_MANUTENCAO",
        ]

    def test_me_sem_cargo_nao_retorna_funcionalidades(self, api_factory):
        """Usuário sem cargo continua autenticado, sem funcionalidades."""
        usuario = Usuario.objects.create(
            username="sem-cargo",
            nome="Sem Cargo",
            email="sem.cargo@email.com",
        )
        request = api_factory.get("/usuarios/me/")
        force_authenticate(request, user=usuario)

        response = UsuarioViewSet.as_view({"get": "me"})(request)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["funcionalidades"] == []
