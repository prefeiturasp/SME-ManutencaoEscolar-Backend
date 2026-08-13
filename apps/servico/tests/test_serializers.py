"""Testes dos serializers da aplicação Serviço."""

import pytest
from rest_framework import serializers

from apps.servico.constants import ServicoErrorMessages
from apps.servico.serializers import (
    ServicoAtualizarSerializer,
    ServicoCriarSerializer,
    ServicoSerializer,
)


class TestServicoCriarSerializer:
    """Testa o serializer de criação de serviços."""

    @pytest.mark.django_db
    def test_deve_validar_dados_corretos(self) -> None:
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

    def test_deve_remover_espacos_do_nome(self) -> None:
        """Deve retirar os espaços antes e depois do nome."""
        serializer = ServicoCriarSerializer()

        nome = serializer.validate_nome("  Pintura  ")

        assert nome == "Pintura"

    def test_deve_rejeitar_nome_apenas_com_espacos(self) -> None:
        """Deve rejeitar o nome que contenha apenas espaços."""
        serializer = ServicoCriarSerializer()

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_nome("   ")

        assert (
            str(exc_info.value.detail[0])
            == ServicoErrorMessages.NOME_OBRIGATORIO
        )

    def test_deve_rejeitar_nome_vazio(self) -> None:
        """Deve utilizar a mensagem configurada para o campo vazio."""
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

    def test_deve_possuir_apenas_campos_de_criacao(self) -> None:
        """Deve disponibilizar apenas os campos aceitos na criação."""
        serializer = ServicoCriarSerializer()

        assert set(serializer.fields) == {
            "nome",
            "status",
        }


class TestServicoAtualizarSerializer:
    """Testa o serializer de atualização de serviços."""

    def test_deve_herdar_serializer_de_criacao(self) -> None:
        """Deve reutilizar as validações do serializer de criação."""
        serializer = ServicoAtualizarSerializer()

        assert isinstance(serializer, ServicoCriarSerializer)

    def test_deve_remover_espacos_do_nome(self) -> None:
        """Deve normalizar o nome durante a atualização."""
        serializer = ServicoAtualizarSerializer()

        nome = serializer.validate_nome("  Elétrica  ")

        assert nome == "Elétrica"

    def test_deve_possuir_campos_atualizaveis(self) -> None:
        """Deve disponibilizar somente os campos atualizáveis."""
        serializer = ServicoAtualizarSerializer()

        assert set(serializer.fields) == {
            "nome",
            "status",
        }


class TestServicoSerializer:
    """Testa o serializer de leitura de serviços."""

    def test_deve_possuir_os_campos_esperados(self) -> None:
        """Deve disponibilizar os campos de leitura e auditoria."""
        serializer = ServicoSerializer()

        assert set(serializer.fields) == {
            "id",
            "uuid",
            "nome",
            "status",
            "criado_por",
            "criado_por_nome",
            "criado_em",
            "atualizado_por",
            "atualizado_por_nome",
            "username",
            "atualizado_em",
        }

    @pytest.mark.parametrize(
        "nome_campo",
        [
            "id",
            "uuid",
            "criado_por",
            "criado_por_nome",
            "criado_em",
            "atualizado_por",
            "atualizado_por_nome",
            "username",
            "atualizado_em",
        ],
    )
    def test_deve_manter_campos_de_auditoria_somente_para_leitura(
        self,
        nome_campo: str,
    ) -> None:
        """Deve impedir alterações nos campos de auditoria."""
        serializer = ServicoSerializer()

        assert serializer.fields[nome_campo].read_only is True

    def test_deve_obter_nome_do_usuario_criador(self) -> None:
        """Deve obter o nome por meio do usuário criador."""
        serializer = ServicoSerializer()

        campo = serializer.fields["criado_por_nome"]

        assert campo.source == "criado_por.nome"
        assert campo.read_only is True
        assert campo.allow_null is True

    def test_deve_obter_nome_do_usuario_atualizador(self) -> None:
        """Deve obter o nome por meio do usuário atualizador."""
        serializer = ServicoSerializer()

        campo = serializer.fields["atualizado_por_nome"]

        assert campo.source == "atualizado_por.nome"
        assert campo.read_only is True
        assert campo.allow_null is True

    def test_deve_obter_username_do_usuario_criador(self) -> None:
        """Deve obter o username por meio do usuário criador."""
        serializer = ServicoSerializer()

        campo = serializer.fields["username"]

        assert campo.source == "criado_por.username"
        assert campo.read_only is True
        assert campo.allow_null is True