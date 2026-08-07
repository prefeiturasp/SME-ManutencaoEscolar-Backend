from uuid import UUID

import pytest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import force_authenticate

from apps.core.api.views import (
    AtualizarTokenView,
    HealthCheckView,
    LoginView,
    LogoutView,
    RedefinirSenhaView,
)
from apps.core.exceptions import (
    EnvioEmailError,
    FalhaAutenticacaoError,
    InternalError,
    SmeIntegracaoError,
    TokenInvalidoError,
)
from apps.usuarios.exceptions import (
    EmailUsuarioNaoEncontradoError,
    UsuarioNaoEncontradoError,
)

pytestmark = pytest.mark.django_db


def test_healthcheck_retorna_ok(api_factory):
    """Deve retornar status da aplicação."""
    request = api_factory.get("/api/v1/health/")

    response = HealthCheckView.as_view()(request)

    assert response.status_code == 200
    assert response.data == {"status": "ok"}


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


def test_atualizar_token_retorna_tokens(api_factory, monkeypatch):
    """Deve atualizar o token com sucesso."""
    monkeypatch.setattr(
        "apps.core.api.views.TokenService.atualizar_token",
        classmethod(lambda cls, refresh: {"username": "1234567"}),
    )

    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.usuario_existe_no_coresso",
        classmethod(lambda cls, username: True),
    )

    monkeypatch.setattr(
        "rest_framework_simplejwt.views.TokenRefreshView.post",
        lambda self, request, *args, **kwargs: Response(
            {"access": "novo-access"},
            status=status.HTTP_200_OK,
        ),
    )

    request = api_factory.post(
        "/token/refresh/",
        {"refresh": "refresh-token"},
        format="json",
    )

    response = AtualizarTokenView.as_view()(request)

    assert response.status_code == 200
    assert response.data == {"access": "novo-access"}


def test_atualizar_token_retorna_401_quando_token_invalido(
    api_factory, monkeypatch
):
    """Deve retornar 401 quando o refresh token for inválido."""

    def mock_atualizar_token(cls, refresh):
        raise TokenInvalidoError(
            title="Token não atualizado.",
            detail="O refresh token é inválido ou já foi revogado.",
        )

    monkeypatch.setattr(
        "apps.core.api.views.TokenService.atualizar_token",
        classmethod(mock_atualizar_token),
    )

    request = api_factory.post(
        "/token/refresh/",
        {"refresh": "refresh-token"},
        format="json",
    )

    response = AtualizarTokenView.as_view()(request)

    assert response.status_code == 401
    assert response.data == {"detail": "Refresh token inválido."}


def test_atualizar_token_retorna_401_quando_usuario_nao_existe(
    api_factory, monkeypatch
):
    """Deve retornar 401 quando o usuário do token não existir."""

    def mock_atualizar_token(cls, refresh):
        raise UsuarioNaoEncontradoError(
            title="Erro",
            detail="Usuário não encontrado.",
        )

    monkeypatch.setattr(
        "apps.core.api.views.TokenService.atualizar_token",
        classmethod(mock_atualizar_token),
    )

    request = api_factory.post(
        "/token/refresh/",
        {"refresh": "refresh-token"},
        format="json",
    )

    response = AtualizarTokenView.as_view()(request)

    assert response.status_code == 401
    assert response.data == {"detail": "Usuário não encontrado."}


def test_logout_retorna_205(api_factory, monkeypatch, usuario_ativo):
    """Deve realizar logout com sucesso."""
    monkeypatch.setattr(
        "apps.core.api.views.TokenService.logout",
        classmethod(lambda cls, usuario_ativo, refresh: None),
    )

    request = api_factory.post(
        "/logout/",
        {"refresh": "refresh-token"},
        format="json",
    )

    force_authenticate(request, user=usuario_ativo)

    request.user = usuario_ativo
    response = LogoutView.as_view()(request)

    assert response.status_code == 205
    assert response.data == {"detail": "Logout realizado com sucesso."}


def test_logout_retorna_401_quando_usuario_invalido(
    api_factory, usuario_ativo
):
    """Deve retornar 401 quando o usuário autenticado for inválido."""
    request = api_factory.post(
        "/logout/",
        {"refresh": "refresh-token"},
        format="json",
    )
    force_authenticate(request, user=usuario_ativo)
    usuario_ativo.id = None
    request.user = usuario_ativo

    response = LogoutView.as_view()(request)

    assert response.status_code == 401
    assert response.data == {"detail": "Usuário autenticado inválido."}


def test_logout_retorna_401_quando_token_invalido(
    api_factory, monkeypatch, usuario_inativo
):
    """Deve retornar 401 quando o refresh token for inválido."""

    def mock_logout(cls, usuario_inativo, refresh):
        raise TokenInvalidoError(
            title="Erro",
            detail="Token inválido.",
        )

    monkeypatch.setattr(
        "apps.core.api.views.TokenService.logout",
        classmethod(mock_logout),
    )

    request = api_factory.post(
        "/logout/",
        {"refresh": "refresh-token"},
        format="json",
    )

    force_authenticate(request, user=usuario_inativo)
    request.user = usuario_inativo

    response = LogoutView.as_view()(request)

    assert response.status_code == 401
    assert response.data == {"detail": "Token inválido."}


def test_atualizar_token_retorna_401_quando_usuario_nao_autorizado(
    api_factory, monkeypatch
):
    """Deve retornar 401 quando o usuário for inválido."""
    monkeypatch.setattr(
        "apps.core.api.views.TokenService.atualizar_token",
        classmethod(
            lambda cls, refresh: {
                "username": "1234567",
            }
        ),
    )

    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.usuario_existe_no_coresso",
        classmethod(lambda cls, username: False),
    )

    request = api_factory.post(
        "/token/refresh/",
        {"refresh": "refresh-token"},
        format="json",
    )

    response = AtualizarTokenView.as_view()(request)

    assert response.status_code == 401
    assert response.data == {"detail": "Usuário não autorizado."}


def test_redefinir_senha_retorna_email_mascarado(
    api_factory,
    monkeypatch,
):
    """Deve enviar o e-mail de recuperação e retornar o e-mail mascarado."""
    usuario = {
        "nome": "João da Silva",
        "email": "joaodasilva@email.com",
        "username": "1234567",
    }

    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.obter_usuario_por_rf_cpf",
        classmethod(lambda cls, _: usuario),
    )

    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.enviar_email_recuperacao_senha",
        staticmethod(lambda usuario: None),
    )

    request = api_factory.post(
        "/usuarios/redefinir-senha/",
        {
            "registro_funcional_ou_cpf": "1234567",
        },
        format="json",
    )

    response = RedefinirSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_200_OK

    assert response.data == {
        "email": "joa********@email.com",
    }


def test_redefinir_senha_usuario_nao_encontrado(
    api_factory,
    monkeypatch,
):
    """Deve retornar 404 quando o usuário não existir."""
    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.obter_usuario_por_rf_cpf",
        classmethod(
            lambda cls, _: (_ for _ in ()).throw(
                UsuarioNaoEncontradoError(
                    title="Usuário não encontrado.",
                    detail="Usuário inexistente.",
                )
            )
        ),
    )

    request = api_factory.post(
        "/usuarios/redefinir-senha/",
        {
            "registro_funcional_ou_cpf": "1234567",
        },
        format="json",
    )

    response = RedefinirSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.data == {
        "title": "Usuário não encontrado.",
        "detail": "Usuário inexistente.",
    }


def test_redefinir_senha_email_nao_encontrado(
    api_factory,
    monkeypatch,
):
    """Deve retornar 404 quando o usuário não possuir e-mail."""
    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.obter_usuario_por_rf_cpf",
        classmethod(
            lambda cls, _: (_ for _ in ()).throw(
                EmailUsuarioNaoEncontradoError(
                    title="E-mail não encontrado.",
                    detail="Usuário sem e-mail.",
                )
            )
        ),
    )

    request = api_factory.post(
        "/usuarios/redefinir-senha/",
        {
            "registro_funcional_ou_cpf": "1234567",
        },
        format="json",
    )

    response = RedefinirSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.data == {
        "title": "E-mail não encontrado.",
        "detail": "Usuário sem e-mail.",
    }


def test_redefinir_senha_erro_envio_email(
    api_factory,
    monkeypatch,
):
    """Deve retornar 503 quando ocorrer erro ao enviar o e-mail."""
    usuario = {
        "nome": "João",
        "email": "joao@email.com",
        "username": "1234567",
    }

    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.obter_usuario_por_rf_cpf",
        classmethod(lambda cls, _: usuario),
    )

    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.enviar_email_recuperacao_senha",
        staticmethod(
            lambda usuario: (_ for _ in ()).throw(
                EnvioEmailError(
                    title="Erro ao enviar e-mail.",
                    detail="Instabilidade no serviço.",
                )
            )
        ),
    )

    request = api_factory.post(
        "/usuarios/redefinir-senha/",
        {
            "registro_funcional_ou_cpf": "1234567",
        },
        format="json",
    )

    response = RedefinirSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    assert response.data == {
        "title": "Erro ao enviar e-mail.",
        "detail": "Instabilidade no serviço.",
    }


def test_redefinir_senha_payload_invalido(
    api_factory,
):
    """Deve retornar 400 quando o payload for inválido."""
    request = api_factory.post(
        "/usuarios/redefinir-senha/",
        {},
        format="json",
    )

    response = RedefinirSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "registro_funcional_ou_cpf" in response.data
