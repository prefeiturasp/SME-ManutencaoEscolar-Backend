import pytest
from rest_framework import serializers

from apps.core.serializers.serializers import (
    AlterarSenhaSerializer,
    AutenticacaoSerializer,
)


class TestAutenticacaoSerializer:
    def test_deve_validar_login_rf(self):
        serializer = AutenticacaoSerializer(
            data={
                "login": "1234567",
                "senha": "123",
            }
        )

        assert serializer.is_valid()

    def test_deve_validar_login_cpf(self):
        serializer = AutenticacaoSerializer(
            data={
                "login": "12345678901",
                "senha": "123",
            }
        )

        assert serializer.is_valid()

    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"login": ""},
            {"senha": ""},
            {"login": "123"},
        ],
    )
    def test_deve_invalidar_payload(self, payload):
        serializer = AutenticacaoSerializer(data=payload)

        assert not serializer.is_valid()

    def test_validate_login_invalido(self):
        serializer = AutenticacaoSerializer()

        with pytest.raises(
            serializers.ValidationError,
            match="O login deve ser um RF com 7 dígitos ou um CPF com 11 "
            "dígitos.",
        ):
            serializer.validate_login("123456")


class TestAlterarSenhaSerializer:
    """Testes para o serializer de alteração de senha."""

    def test_dados_validos(self):
        """Deve validar os dados corretamente."""
        data = {
            "registro_funcional_ou_cpf": "1234567",
            "token": "token-123",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "NovaSenha123!",
        }

        serializer = AlterarSenhaSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data == data

    def test_deve_aceitar_cpf_com_11_digitos(self):
        """Deve aceitar CPF com 11 dígitos."""
        data = {
            "registro_funcional_ou_cpf": "12345678901",
            "token": "token-123",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "NovaSenha123!",
        }

        serializer = AlterarSenhaSerializer(data=data)

        assert serializer.is_valid()

    @pytest.mark.parametrize(
        "registro",
        ["12345678", "123456789", "1234567890"],
    )
    def test_deve_rejeitar_registro_com_tamanho_invalido(self, registro):
        """Deve rejeitar RF ou CPF com quantidade de dígitos inválida."""
        data = {
            "registro_funcional_ou_cpf": registro,
            "token": "token-123",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "NovaSenha123!",
        }

        serializer = AlterarSenhaSerializer(data=data)

        assert not serializer.is_valid()
        assert serializer.errors["registro_funcional_ou_cpf"] == [
            (
                "O registro_funcional_ou_cpf deve ser um RF com 7 dígitos "
                "ou um CPF com 11 dígitos."
            )
        ]

    def test_deve_rejeitar_senhas_diferentes(self):
        """Deve rejeitar quando senha e confirmação forem diferentes."""
        data = {
            "registro_funcional_ou_cpf": "1234567",
            "token": "token-123",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "OutraSenha123!",
        }

        serializer = AlterarSenhaSerializer(data=data)

        assert not serializer.is_valid()

        assert serializer.errors["confirmacao_senha"] == [
            "As senhas não coincidem."
        ]

    @pytest.mark.parametrize(
        "campo",
        [
            "registro_funcional_ou_cpf",
            "token",
            "senha",
            "confirmacao_senha",
        ],
    )
    def test_deve_rejeitar_campo_obrigatorio_ausente(self, campo):
        """Deve rejeitar requisição sem campos obrigatórios."""
        data = {
            "registro_funcional_ou_cpf": "1234567",
            "token": "token-123",
            "senha": "NovaSenha123!",
            "confirmacao_senha": "NovaSenha123!",
        }

        data.pop(campo)

        serializer = AlterarSenhaSerializer(data=data)

        assert not serializer.is_valid()
        assert campo in serializer.errors
