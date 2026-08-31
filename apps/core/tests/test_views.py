from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import force_authenticate

from apps.core.api.views import (
    AlterarSenhaView,
    AnexoView,
    AtualizarTokenView,
    HealthCheckView,
    LoginView,
    LogoutView,
    RedefinirSenhaView,
)
from apps.core.exceptions import (
    AnexoArquivoError,
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


def test_login_retorna_payload_autenticado(
    api_factory,
    monkeypatch,
) -> None:
    """Deve retornar o payload autenticado."""
    dados = {
        "refresh": "refresh-token",
        "access": "access-token",
        "access_expires_in": 60,
        "refresh_expires_in": 604800,
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

    assert response.status_code == status.HTTP_200_OK
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

    def raise_usuario_nao_encontado_error(*args, **kwargs):
        raise UsuarioNaoEncontradoError(
            title="Usuário não encontrado.",
            detail="Verifique se o RF ou CPF digitados estão corretos e "
            "tente novamente",
        )

    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.obter_usuario_por_rf_cpf",
        classmethod(raise_usuario_nao_encontado_error),
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
        "detail": "Verifique se o RF ou CPF digitados estão corretos e "
        "tente novamente",
    }


def test_redefinir_senha_email_nao_encontrado(
    api_factory,
    monkeypatch,
):
    """Deve retornar 404 quando o usuário não possuir e-mail."""

    def raise_email_usuario_error(*args, **kwargs):
        raise EmailUsuarioNaoEncontradoError(
            title="E-mail não encontrado.",
            detail="Não foi encontrado e-mail para esse RF ou CPF.",
        )

    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.obter_usuario_por_rf_cpf",
        classmethod(raise_email_usuario_error),
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
        "detail": "Não foi encontrado e-mail para esse RF ou CPF.",
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

    def raise_enio_email_error(*args, **kwargs):
        raise EnvioEmailError(
            title="Erro ao enviar e-mail.",
            detail="Parece que estamos com uma instabilidade no momento. "
            "Tente novamnete daqui a pouco",
        )

    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.obter_usuario_por_rf_cpf",
        classmethod(lambda cls, _: usuario),
    )

    monkeypatch.setattr(
        "apps.usuarios.api.views.UsuarioService.enviar_email_recuperacao_senha",
        staticmethod(raise_enio_email_error),
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
        "detail": "Parece que estamos com uma instabilidade no momento. "
        "Tente novamnete daqui a pouco",
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


def test_alterar_senha_retorna_sucesso(api_factory, monkeypatch):
    """Deve alterar a senha com sucesso."""
    monkeypatch.setattr(
        "apps.core.api.views.TokenService.validar_token_recuperar_senha",
        classmethod(lambda cls, username, token: None),
    )

    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.alterar_senha_no_coresso",
        classmethod(lambda cls, login, nova_senha: None),
    )

    request = api_factory.post(
        "/usuarios/alterar-senha/",
        {
            "registro_funcional_ou_cpf": "1234567",
            "token": "token-123",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "NovaSenha123!",
        },
        format="json",
    )

    response = AlterarSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"detail": "Senha alterada com sucesso."}


def test_alterar_senha_retorna_404_quando_usuario_nao_existe(
    api_factory, monkeypatch
):
    """Deve retornar 404 quando o usuário não existir."""

    def raise_usuario_nao_encontrado(*args, **kwargs):
        raise UsuarioNaoEncontradoError(
            title="Usuário não encontrado.",
            detail="Usuário não encontrado ou inválido",
        )

    monkeypatch.setattr(
        "apps.core.api.views.TokenService.validar_token_recuperar_senha",
        classmethod(raise_usuario_nao_encontrado),
    )

    request = api_factory.post(
        "/usuarios/alterar-senha/",
        {
            "registro_funcional_ou_cpf": "1234567",
            "token": "token-123",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "NovaSenha123!",
        },
        format="json",
    )

    response = AlterarSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == {
        "title": "Usuário não encontrado.",
        "detail": "Usuário não encontrado ou inválido",
    }


def test_alterar_senha_retorna_401_quando_token_invalido(
    api_factory, monkeypatch
):
    """Deve retornar 401 quando o token for inválido."""

    def raise_token_invalido(*args, **kwargs):
        raise TokenInvalidoError(
            title="Token inválido.",
            detail=(
                "Por segurança, o link de redefinição tem validade de "
                "6 horas. Solicite um novo para redefinir sua senha."
            ),
        )

    monkeypatch.setattr(
        "apps.core.api.views.TokenService.validar_token_recuperar_senha",
        classmethod(raise_token_invalido),
    )

    request = api_factory.post(
        "/usuarios/alterar-senha/",
        {
            "registro_funcional_ou_cpf": "1234567",
            "token": "token-invalido",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "NovaSenha123!",
        },
        format="json",
    )

    response = AlterarSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {
        "title": "Token inválido.",
        "detail": (
            "Por segurança, o link de redefinição tem validade de "
            "6 horas. Solicite um novo para redefinir sua senha."
        ),
    }


def test_alterar_senha_retorna_401_quando_falha_autenticacao(
    api_factory, monkeypatch
):
    """Deve retornar 401 quando ocorrer falha de autenticação."""
    monkeypatch.setattr(
        "apps.core.api.views.TokenService.validar_token_recuperar_senha",
        classmethod(lambda cls, username, token: None),
    )

    def raise_falha_autenticacao(*args, **kwargs):
        raise FalhaAutenticacaoError("Usuário ou senha incorretos.")

    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.alterar_senha_no_coresso",
        classmethod(raise_falha_autenticacao),
    )

    request = api_factory.post(
        "/usuarios/alterar-senha/",
        {
            "registro_funcional_ou_cpf": "1234567",
            "token": "token-123",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "NovaSenha123!",
        },
        format="json",
    )

    response = AlterarSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {
        "title": "Erro ao alterar senha",
        "detail": "Usuário ou senha incorretos.",
    }


def test_alterar_senha_retorna_502_quando_eol_esta_indisponivel(
    api_factory, monkeypatch
):
    """Deve retornar 502 quando ocorrer falha na integração."""
    monkeypatch.setattr(
        "apps.core.api.views.TokenService.validar_token_recuperar_senha",
        classmethod(lambda cls, username, token: None),
    )

    def raise_sme_integracao(*args, **kwargs):
        raise SmeIntegracaoError("Erro ao alterar a senha no servidor.")

    monkeypatch.setattr(
        "apps.core.api.views.AutenticacaoEOLService.alterar_senha_no_coresso",
        classmethod(raise_sme_integracao),
    )

    request = api_factory.post(
        "/usuarios/alterar-senha/",
        {
            "registro_funcional_ou_cpf": "1234567",
            "token": "token-123",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "NovaSenha123!",
        },
        format="json",
    )

    response = AlterarSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert response.data == {
        "title": "Erro ao alterar senha",
        "detail": "Erro ao alterar a senha no servidor.",
    }


def test_alterar_senha_payload_invalido(api_factory):
    """Deve retornar 400 quando o payload for inválido."""
    request = api_factory.post(
        "/usuarios/alterar-senha/",
        {},
        format="json",
    )

    response = AlterarSenhaView.as_view()(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_post_cria_anexo_sem_enviar_arquivo_para_o_minio(
    api_factory, usuario_ativo, arquivo
):
    """Verifica se cria o anexo sem realizar upload no MinIO."""
    anexo = {
        "uuid": "12345678-1234-5678-1234-567812345678",
        "nome": "documento.pdf",
        "tipo": "documento",
        "tipo_mime": "application/pdf",
        "tamanho": 9,
        "url": "https://minio.local/documento.pdf",
    }
    request = api_factory.post(
        "/upload/",
        {"arquivo": arquivo},
        format="multipart",
    )
    force_authenticate(request, user=usuario_ativo)

    service = Mock()
    service.enviar_arquivo.return_value = anexo

    with (
        patch(
            "apps.core.api.views.AnexoService",
            return_value=service,
        ) as service_class,
        patch(
            "apps.core.models.anexo.Anexo.arquivo.field.storage._save",
            autospec=True,
            return_value="arquivos/documento.pdf",
        ) as minio_save,
    ):
        response = AnexoView.as_view()(request)

    assert response.status_code == 201
    assert response.data["nome"] == "documento.pdf"
    service_class.assert_called_once_with()
    service.enviar_arquivo.assert_called_once()
    minio_save.assert_not_called()


def test_post_rejeita_usuario_nao_autenticado(api_factory, arquivo):
    """Verifica se rejeita usuário sem identificador."""
    request = api_factory.post(
        "/upload/",
        {"arquivo": arquivo},
        format="multipart",
    )
    usuario_sem_id = SimpleNamespace(
        id=None,
        is_authenticated=True,
    )
    force_authenticate(request, user=usuario_sem_id)

    with patch("apps.core.api.views.AnexoService") as service_class:
        response = AnexoView.as_view()(request)

    assert response.status_code == 401
    assert response.data == {"detail": "Usuário não autenticado."}
    service_class.assert_not_called()


def test_post_retorna_400_para_erro_de_arquivo(
    api_factory, usuario_ativo, arquivo
):
    """Verifica se retorna 400 quando ocorre erro no arquivo."""
    request = api_factory.post(
        "/upload/",
        {"arquivo": arquivo},
        format="multipart",
    )
    force_authenticate(request, user=usuario_ativo)

    erro = AnexoArquivoError(
        title="Tipo inválido",
        detail="Arquivo não permitido.",
    )

    service = Mock()
    service.enviar_arquivo.side_effect = erro

    with patch(
        "apps.core.api.views.AnexoService",
        return_value=service,
    ):
        response = AnexoView.as_view()(request)

    assert response.status_code == 400
    assert response.data == {
        "title": "Tipo inválido",
        "detail": "Arquivo não permitido.",
    }


def test_post_retorna_404_para_usuario_inexistente(
    api_factory, usuario_ativo, arquivo
):
    """Verifica se retorna 404 quando o usuário não é encontrado."""
    request = api_factory.post(
        "/upload/",
        {"arquivo": arquivo},
        format="multipart",
    )
    force_authenticate(request, user=usuario_ativo)

    erro = UsuarioNaoEncontradoError(
        title="Usuário não encontrado",
        detail="Usuário inexistente.",
    )

    service = Mock()
    service.enviar_arquivo.side_effect = erro

    with patch(
        "apps.core.api.views.AnexoService",
        return_value=service,
    ):
        response = AnexoView.as_view()(request)

    assert response.status_code == 404
    assert response.data == {
        "title": "Usuário não encontrado",
        "detail": "Usuário inexistente.",
    }
