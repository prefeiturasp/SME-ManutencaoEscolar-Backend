import pytest
from rest_framework import serializers

from apps.core.serializers import AutenticacaoSerializer


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
