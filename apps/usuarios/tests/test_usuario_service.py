from unittest.mock import patch

import pytest
from django.db.models import ObjectDoesNotExist

from apps.core.exceptions import EnvioEmailError, TokenInvalidoError
from apps.usuarios.exceptions import (
    EmailUsuarioNaoEncontradoError,
    UsuarioNaoEncontradoError,
)
from apps.usuarios.services.usuario_service import UsuarioService

pytestmark = pytest.mark.django_db


class TestUsuarioService:
    @patch(
        "apps.usuarios.services.usuario_service.UsuarioRepository."
        "atualizar_ou_criar"
    )
    @patch(
        "apps.usuarios.services.usuario_service.CargoEOLRepository."
        "buscar_por_codigo"
    )
    def test_sincronizar_usuario(
        self,
        mock_buscar_cargo,
        mock_atualizar,
    ):
        mock_buscar_cargo.return_value = {
            "codigo": 3360,
        }

        mock_atualizar.return_value = {
            "id": 1,
        }

        resultado = UsuarioService.sincronizar_usuario(
            dados_usuario={"nome": "João"},
            dados_cargo={"codigo_cargo": "3360"},
        )

        assert resultado == {"id": 1}

        mock_buscar_cargo.assert_called_once_with(3360)

        mock_atualizar.assert_called_once_with(
            dados_usuario={"nome": "João"},
            codigo_cargo="3360",
        )

    @patch(
        "apps.usuarios.services.usuario_service.UsuarioRepository."
        "atualizar_ou_criar"
    )
    @patch(
        "apps.usuarios.services.usuario_service.CargoEOLRepository."
        "buscar_por_codigo"
    )
    def test_sincronizar_usuario_codigo_cargo_invalido(
        self,
        mock_buscar_cargo,
        mock_atualizar,
    ):
        mock_buscar_cargo.return_value = {
            "codigo": 3360,
        }

        UsuarioService.sincronizar_usuario(
            dados_usuario={"nome": "João"},
            dados_cargo={"codigo_cargo": "abc"},
        )

        assert mock_buscar_cargo.call_count == 1
        mock_buscar_cargo.assert_called_with(3360)

    @patch(
        "apps.usuarios.services.usuario_service.UsuarioRepository."
        "atualizar_ou_criar"
    )
    @patch(
        "apps.usuarios.services.usuario_service.CargoEOLRepository."
        "buscar_por_codigo"
    )
    def test_sincronizar_usuario_codigo_none(
        self,
        mock_buscar_cargo,
        mock_atualizar,
    ):
        mock_buscar_cargo.return_value = {
            "codigo": 3360,
        }

        UsuarioService.sincronizar_usuario(
            dados_usuario={},
            dados_cargo={"codigo_cargo": None},
        )

        mock_buscar_cargo.assert_called_once_with(3360)

    @patch(
        "apps.usuarios.services.usuario_service.CargoEOLRepository."
        "buscar_por_codigo"
    )
    def test_sincronizar_usuario_cargo_inexistente(
        self,
        mock_buscar_cargo,
    ):
        mock_buscar_cargo.return_value = None

        with pytest.raises(
            ValueError,
            match="Cargo não encontrado",
        ):
            UsuarioService.sincronizar_usuario(
                dados_usuario={},
                dados_cargo={"codigo_cargo": "3360"},
            )

    def test_deve_retornar_usuario(self, usuario_ativo, usuario_ativo_dict):
        """Deve retornar os dados do usuário."""
        resultado = UsuarioService.obter_usuario_por_rf_cpf(usuario_ativo.cpf)
        assert resultado == usuario_ativo_dict

    def test_deve_lancar_erro_quando_email_nao_existir(self, usuario_ativo):
        """Deve lançar erro quando o usuário não possuir e-mail."""
        usuario_ativo.email = ""
        usuario_ativo.save()

        with pytest.raises(
            EmailUsuarioNaoEncontradoError,
        ):
            UsuarioService.obter_usuario_por_rf_cpf(usuario_ativo.cpf)

    def test_deve_lancar_erro_quando_usuario_nao_existir(
        self,
    ):
        """Deve lançar erro quando o usuário não existir."""
        with pytest.raises(
            UsuarioNaoEncontradoError,
        ):
            UsuarioService.obter_usuario_por_rf_cpf("1111111")

    @patch("apps.usuarios.services.usuario_service.EmailService.enviar")
    @patch(
        "apps.usuarios.services.usuario_service.UsuarioRepository."
        "gerar_token_recuperar_senha"
    )
    @patch("apps.usuarios.services.usuario_service.settings")
    def test_deve_enviar_email(
        self,
        settings_mock,
        gerar_token_mock,
        enviar_email_mock,
        usuario_ativo_dict,
    ):
        """Deve enviar o e-mail de recuperação."""
        settings_mock.FRONTEND_URL = "https://frontend"
        username = usuario_ativo_dict["username"]
        token = "redefir-senha"

        gerar_token_mock.return_value = {
            "token_recuperacao": token,
        }

        UsuarioService.enviar_email_recuperacao_senha(
            usuario_ativo_dict,
        )

        gerar_token_mock.assert_called_once_with(username)

        enviar_email_mock.assert_called_once_with(
            assunto="Recuperação de senha",
            template="recuperar_senha.html",
            contexto={
                "nome": usuario_ativo_dict["nome"],
                "url": (
                    f"https://frontend/redefinir-senha/?id={username}&"
                    f"token={token}"
                ),
                "username": username,
            },
            destinatarios=[
                usuario_ativo_dict["email"],
            ],
        )

    @patch("apps.usuarios.services.usuario_service.logger")
    @patch("apps.usuarios.services.usuario_service.EmailService.enviar")
    @patch(
        "apps.usuarios.services.usuario_service.UsuarioRepository."
        "gerar_token_recuperar_senha"
    )
    @patch("apps.usuarios.services.usuario_service.settings")
    def test_deve_lancar_erro_quando_envio_falhar(
        self,
        settings_mock,
        gerar_token_mock,
        enviar_email_mock,
        logger_mock,
        usuario_ativo_dict,
    ):
        """Deve lançar EnvioEmailError quando ocorrer erro no envio."""
        settings_mock.FRONTEND_URL = "https://frontend"
        username = usuario_ativo_dict["username"]
        token = "redefir-senha"

        gerar_token_mock.return_value = {
            "token_recuperacao": token,
        }

        UsuarioService.enviar_email_recuperacao_senha(
            usuario_ativo_dict,
        )
        gerar_token_mock.assert_called_once_with(username)
        enviar_email_mock.side_effect = Exception()
        with pytest.raises(
            EnvioEmailError,
        ):
            UsuarioService.enviar_email_recuperacao_senha(
                usuario_ativo_dict,
            )

        logger_mock.exception.assert_called_once_with(
            "Erro ao enviar e-mail para o usuário '%s'.",
            username,
        )

    @patch(
        "apps.usuarios.services.usuario_service.UsuarioRepository."
        "verificar_token_atualizar_senha"
    )
    def test_validar_token(self, verificar_token_mock, usuario_ativo_dict):
        """Deve validar o token de recuperação de senha."""
        username = usuario_ativo_dict["username"]
        token = "token-123"

        UsuarioService.validar_token(
            username=username,
            token=token,
        )

        verificar_token_mock.assert_called_once_with(
            username=username,
            token=token,
        )

    @patch(
        "apps.usuarios.services.usuario_service.UsuarioRepository."
        "verificar_token_atualizar_senha"
    )
    def test_validar_token_usuario_nao_encontrado(self, verificar_token_mock):
        """Deve lançar erro quando o usuário não for encontrado."""
        verificar_token_mock.side_effect = ObjectDoesNotExist

        with pytest.raises(UsuarioNaoEncontradoError) as exc:
            UsuarioService.validar_token(
                username="1234567",
                token="token-123",
            )

        assert exc.value.title == "Usuário não encontrado."
        assert exc.value.detail == "Usuário não encontrado ou inválido"

        verificar_token_mock.assert_called_once_with(
            username="1234567",
            token="token-123",
        )

    @patch(
        "apps.usuarios.services.usuario_service.UsuarioRepository."
        "verificar_token_atualizar_senha"
    )
    def test_validar_token_invalido(self, verificar_token_mock):
        """Deve lançar erro quando o token for inválido ou expirado."""
        verificar_token_mock.side_effect = TokenInvalidoError(
            title="Token inválido.",
            detail="Token inválido.",
        )

        with pytest.raises(TokenInvalidoError) as exc:
            UsuarioService.validar_token(
                username="1234567",
                token="token-invalido",
            )

        assert exc.value.title == "O link está expirado!"
        assert (
            exc.value.detail
            == "Por segurança, o link de redefinição tem validade de "
            "6 horas. Solicite um novo para redefinir sua senha."
        )

        verificar_token_mock.assert_called_once_with(
            username="1234567",
            token="token-invalido",
        )
