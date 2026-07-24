"""Testes das views da aplicação Serviço."""

from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.servico.api.views import (
    ServicoInstabilidadeError,
    ServicoViewSet,
)
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.serializers import ServicoCriarSerializer


class TestServicoViewSet:
    """Testes para ServicoViewSet."""

    def setup_method(self):
        """Configura a view e o serializer usados nos testes."""
        self.view = ServicoViewSet()
        self.view.service = MagicMock()

        self.serializer = MagicMock()
        self.serializer.validated_data = {
            "nome": "Pintura",
            "status": True,
        }

    def test_deve_retornar_serializer_de_criacao_na_action_create(self):
        """Deve usar o serializer de criação no cadastro."""
        self.view.action = "create"

        serializer_class = self.view.get_serializer_class()

        assert serializer_class is ServicoCriarSerializer

    def test_deve_retornar_serializer_padrao_em_outra_action(self):
        """Deve retornar o serializer configurado para outra ação."""
        self.view.action = "list"

        serializer_class = self.view.get_serializer_class()

        assert serializer_class is ServicoCriarSerializer

    def test_deve_delegar_criacao_ao_service(self):
        """Deve delegar a criação e atribuir a instância."""
        servico = MagicMock()
        self.view.service.criar.return_value = servico

        self.view.perform_create(self.serializer)

        self.view.service.criar.assert_called_once_with(
            self.serializer.validated_data
        )
        assert self.serializer.instance is servico

    def test_deve_converter_erro_de_servico_duplicado(self):
        """Deve converter erro de duplicidade em erro do DRF."""
        self.view.service.criar.side_effect = ServicoJaCadastradoError(
            title="Serviço já cadastrado",
            detail="Já existe um serviço com esse nome.",
        )

        with pytest.raises(DRFValidationError) as exc_info:
            self.view.perform_create(self.serializer)

        assert exc_info.value.detail["title"] == "Serviço já cadastrado"
        assert (
            exc_info.value.detail["detail"]
            == "Já existe um serviço com esse nome."
        )

    def test_deve_converter_validation_error_com_message_dict(self):
        """Deve converter erro Django contendo dicionário."""
        self.view.service.criar.side_effect = DjangoValidationError(
            {"nome": ["Nome inválido."]}
        )

        with pytest.raises(DRFValidationError) as exc_info:
            self.view.perform_create(self.serializer)

        assert "nome" in exc_info.value.detail

    def test_deve_converter_validation_error_com_messages(self):
        """Deve converter erro Django contendo lista de mensagens."""
        self.view.service.criar.side_effect = DjangoValidationError(
            ["Dados inválidos."]
        )

        with pytest.raises(DRFValidationError) as exc_info:
            self.view.perform_create(self.serializer)

        assert "Dados inválidos." in str(exc_info.value.detail)

    def test_deve_converter_erro_inesperado_em_instabilidade(self):
        """Deve retornar instabilidade para erro inesperado."""
        self.view.service.criar.side_effect = RuntimeError("Erro inesperado")

        with pytest.raises(ServicoInstabilidadeError):
            self.view.perform_create(self.serializer)
