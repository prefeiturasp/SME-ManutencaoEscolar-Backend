"""Testes das views do domínio Serviço."""

from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny
from rest_framework.serializers import BaseSerializer

from apps.core.pagination import PaginacaoPadrao
from apps.servico.api.views import (
    ServicoInstabilidadeError,
    ServicoViewSet,
)
from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.filters import ServicoFilter
from apps.servico.serializers import (
    ServicoCriarSerializer,
    ServicoSerializer,
)
from apps.servico.services.servico_service import ServicoService


class TestServicoViewSet:
    """Testes para ServicoViewSet."""

    def setup_method(self):
        """Configura a view e suas dependências."""
        self.service = Mock(spec=ServicoService)

        with patch(
            "apps.servico.api.views.ServicoService",
            return_value=self.service,
        ):
            self.view = ServicoViewSet()

    @staticmethod
    def criar_serializer(dados: dict) -> Mock:
        """Cria um serializer simulado com dados validados."""
        serializer = Mock(spec=BaseSerializer)
        serializer.validated_data = dados
        serializer.instance = None

        return serializer

    def test_deve_criar_service_ao_inicializar_view(self):
        """Deve criar o service utilizado pela view."""
        service = Mock(spec=ServicoService)

        with patch(
            "apps.servico.api.views.ServicoService",
            return_value=service,
        ) as service_class:
            view = ServicoViewSet()

        service_class.assert_called_once_with()
        assert view.service is service

    def test_deve_possuir_configuracoes_da_view(self):
        """Deve utilizar as configurações esperadas."""
        assert ServicoViewSet.permission_classes == [AllowAny]
        assert ServicoViewSet.http_method_names == [
            "post",
            "options",
            "get",
        ]
        assert ServicoViewSet.filter_backends == [DjangoFilterBackend]
        assert ServicoViewSet.filterset_class is ServicoFilter
        assert ServicoViewSet.pagination_class is PaginacaoPadrao

    def test_deve_retornar_serializer_de_criacao_na_action_create(self):
        """Deve retornar o serializer de criação no cadastro."""
        self.view.action = "create"

        serializer_class = self.view.get_serializer_class()

        assert serializer_class is ServicoCriarSerializer

    def test_deve_retornar_serializer_de_listagem_na_action_list(self):
        """Deve retornar o serializer de leitura na listagem."""
        self.view.action = "list"

        serializer_class = self.view.get_serializer_class()

        assert serializer_class is ServicoSerializer

    def test_deve_retornar_serializer_de_leitura_em_outra_action(self):
        """Deve usar o serializer de leitura nas demais ações."""
        self.view.action = "retrieve"

        serializer_class = self.view.get_serializer_class()

        assert serializer_class is ServicoSerializer

    def test_deve_criar_servico_e_definir_instancia_no_serializer(self):
        """Deve delegar a criação ao service."""
        dados = {
            "nome": "Pintura",
            "status": True,
        }
        servico = Mock()
        serializer = self.criar_serializer(dados)

        self.service.criar.return_value = servico

        self.view.perform_create(serializer)

        self.service.criar.assert_called_once_with(dados)
        assert serializer.instance is servico

    def test_deve_converter_erro_de_servico_duplicado(self):
        """Deve converter duplicidade em erro de validação do DRF."""
        serializer = self.criar_serializer(
            {
                "nome": "Pintura",
                "status": True,
            }
        )
        erro = ServicoJaCadastradoError(
            title=ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO,
            detail=ServicoErrorMessages.NOME_JA_CADASTRADO,
        )

        self.service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            self.view.perform_create(serializer)

        detalhe = exc_info.value.detail

        assert (
            str(detalhe["title"])
            == ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO
        )
        assert (
            str(detalhe["detail"]) == ServicoErrorMessages.NOME_JA_CADASTRADO
        )
        assert exc_info.value.__cause__ is erro
        assert serializer.instance is None

    def test_deve_converter_django_validation_error_com_message_dict(self):
        """Deve converter erros de campos do Django para o DRF."""
        serializer = self.criar_serializer(
            {
                "nome": "",
                "status": True,
            }
        )
        erro = DjangoValidationError(
            {
                "nome": ["Nome inválido."],
                "status": ["Status inválido."],
            }
        )

        self.service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            self.view.perform_create(serializer)

        detalhe = exc_info.value.detail

        assert [str(item) for item in detalhe["nome"]] == ["Nome inválido."]
        assert [str(item) for item in detalhe["status"]] == [
            "Status inválido."
        ]
        assert exc_info.value.__cause__ is erro
        assert serializer.instance is None

    def test_deve_converter_django_validation_error_com_messages(self):
        """Deve converter erros gerais do Django para o DRF."""
        serializer = self.criar_serializer(
            {
                "nome": "Pintura",
                "status": True,
            }
        )
        erro = DjangoValidationError(
            [
                "Primeiro erro.",
                "Segundo erro.",
            ]
        )

        self.service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            self.view.perform_create(serializer)

        mensagens = [str(mensagem) for mensagem in exc_info.value.detail]

        assert mensagens == [
            "Primeiro erro.",
            "Segundo erro.",
        ]
        assert exc_info.value.__cause__ is erro
        assert serializer.instance is None

    def test_deve_converter_erro_inesperado_em_instabilidade(self):
        """Deve ocultar erros inesperados como instabilidade."""
        serializer = self.criar_serializer(
            {
                "nome": "Pintura",
                "status": True,
            }
        )
        erro = RuntimeError("Erro interno do banco")

        self.service.criar.side_effect = erro

        with pytest.raises(ServicoInstabilidadeError) as exc_info:
            self.view.perform_create(serializer)

        detalhe = exc_info.value.detail

        assert exc_info.value.status_code == 500
        assert exc_info.value.default_code == "servico_instabilidade"
        assert str(detalhe["title"]) == "Erro"
        assert str(detalhe["detail"]) == ServicoErrorMessages.INSTABILIDADE
        assert exc_info.value.__cause__ is erro
        assert serializer.instance is None


class TestServicoInstabilidadeError:
    """Testes para ServicoInstabilidadeError."""

    def test_deve_possuir_configuracoes_corretas(self):
        """Deve representar uma falha interna do serviço."""
        assert ServicoInstabilidadeError.status_code == 500
        assert (
            ServicoInstabilidadeError.default_detail
            == ServicoErrorMessages.INSTABILIDADE
        )
        assert (
            ServicoInstabilidadeError.default_code == "servico_instabilidade"
        )
