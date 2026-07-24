from unittest.mock import patch

import pytest

from apps.usuarios.services.usuario_service import UsuarioService


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
