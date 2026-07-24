"""Testes dos serializers da aplicação Serviço."""

import pytest
from rest_framework import serializers

from apps.servico.constants import ServicoErrorMessages
from apps.servico.serializers import (
    ServicoCriarSerializer,
    ServicoSerializer,
)


class TestServicoCriarSerializer:
    """Testes para ServicoCriarSerializer."""

    def test_deve_validar_dados_corretos(self):
        """Deve aceitar os dados válidos do serviço."""
        serializer = ServicoCriarSerializer(
            data={
                "nome": "Pintura",
                "status": True,
            }
        )

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["nome"] == "Pintura"
        assert serializer.validated_data["status"] is True

    def test_deve_remover_espacos_do_nome(self):
        """Deve retirar espaços antes e depois do nome."""
        serializer = ServicoCriarSerializer()

        nome = serializer.validate_nome("  Pintura  ")

        assert nome == "Pintura"

    def test_deve_rejeitar_nome_apenas_com_espacos(self):
        """Deve rejeitar nome vazio após retirar os espaços."""
        serializer = ServicoCriarSerializer()

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_nome("   ")

        assert (
            str(exc_info.value.detail[0])
            == ServicoErrorMessages.NOME_OBRIGATORIO
        )

    def test_deve_rejeitar_nome_vazio(self):
        """Deve utilizar a mensagem configurada para campo vazio."""
        serializer = ServicoCriarSerializer(
            data={
                "nome": "",
                "status": True,
            }
        )

        assert not serializer.is_valid()
        assert (
            str(serializer.errors["nome"][0])
            == ServicoErrorMessages.NOME_OBRIGATORIO
        )


class TestServicoSerializer:
    """Testes para ServicoSerializer."""

    def test_deve_possuir_os_campos_esperados(self):
        """Deve disponibilizar os campos de leitura do serviço."""
        serializer = ServicoSerializer()

        assert set(serializer.fields) == {
            "id",
            "uuid",
            "nome",
            "status",
        }
