"""Testes das views DRF do domínio Serviço."""

from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import PaginacaoPadrao
from apps.servico.api.views import (
    ServicoInstabilidadeError,
    ServicoViewSet,
)
from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.filters import ServicoFilter
from apps.servico.models import Servico
from apps.servico.serializers import (
    ServicoAtualizarSerializer,
    ServicoCriarSerializer,
    ServicoSerializer,
)
from apps.servico.services.servico_service import ServicoService


class TestServicoInstabilidadeError:
    """Testa a exceção de instabilidade de serviços."""

    def test_deve_possuir_configuracao_esperada(self) -> None:
        """Deve utilizar status HTTP 500 e código específico."""
        assert ServicoInstabilidadeError.status_code == 500
        assert (
            ServicoInstabilidadeError.default_detail
            == ServicoErrorMessages.INSTABILIDADE
        )
        assert (
            ServicoInstabilidadeError.default_code
            == "servico_instabilidade"
        )


class TestServicoViewSet:
    """Testa a view responsável pelo domínio Serviço."""

    @staticmethod
    def criar_view_com_usuario(
        usuario_id: int = 10,
    ) -> ServicoViewSet:
        """Cria uma view com um usuário autenticado simulado."""
        view = ServicoViewSet()
        view.request = Mock()
        view.request.user.pk = usuario_id
        view.service = Mock(spec=ServicoService)

        return view

    @staticmethod
    def criar_serializer(
        dados: dict | None = None,
        instancia: Servico | None = None,
    ) -> Mock:
        """Cria um serializer simulado para os testes da view."""
        serializer = Mock()
        serializer.validated_data = dados or {}
        serializer.instance = instancia

        return serializer

    @patch("apps.servico.api.views.ServicoService")
    def test_deve_criar_service_ao_instanciar_view(
        self,
        mock_service_class: Mock,
    ) -> None:
        """Deve criar o service utilizado pela view."""
        service = mock_service_class.return_value

        view = ServicoViewSet()

        assert view.service is service
        mock_service_class.assert_called_once_with()

    def test_deve_possuir_configuracoes_da_view(self) -> None:
        """Deve possuir as configurações esperadas."""
        view = ServicoViewSet()

        assert view.http_method_names == [
            "get",
            "post",
            "patch",
            "options",
        ]
        assert view.lookup_field == "uuid"
        assert view.filter_backends == [DjangoFilterBackend]
        assert view.filterset_class is ServicoFilter
        assert view.pagination_class is PaginacaoPadrao
        assert view.permission_classes == [IsAuthenticated]

    @pytest.mark.parametrize(
        ("acao", "serializer_esperado"),
        [
            ("create", ServicoCriarSerializer),
            ("update", ServicoAtualizarSerializer),
            ("partial_update", ServicoAtualizarSerializer),
            ("list", ServicoSerializer),
            ("retrieve", ServicoSerializer),
        ],
    )
    def test_deve_retornar_serializer_conforme_acao(
        self,
        acao: str,
        serializer_esperado: type,
    ) -> None:
        """Deve selecionar o serializer correspondente à ação."""
        view = ServicoViewSet()
        view.action = acao

        resultado = view.get_serializer_class()

        assert resultado is serializer_esperado

    def test_deve_criar_servico_e_definir_instancia(
        self,
    ) -> None:
        """Deve delegar a criação e definir a instância criada."""
        view = self.criar_view_com_usuario(usuario_id=10)
        serializer = self.criar_serializer(
            dados={
                "nome": "Pintura",
                "status": True,
            }
        )
        servico_criado = Mock(spec=Servico)
        view.service.criar.return_value = servico_criado

        view.perform_create(serializer)

        view.service.criar.assert_called_once_with(
            {
                "nome": "Pintura",
                "status": True,
            },
            usuario_id=10,
        )
        assert serializer.instance is servico_criado

    def test_deve_converter_erro_de_nome_duplicado_na_criacao(
        self,
    ) -> None:
        """Deve converter erro de duplicidade em erro de validação."""
        view = self.criar_view_com_usuario()
        serializer = self.criar_serializer(
            dados={
                "nome": "Pintura",
                "status": True,
            }
        )
        erro = ServicoJaCadastradoError(
            title=ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO,
            detail=ServicoErrorMessages.NOME_JA_CADASTRADO,
        )
        view.service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_create(serializer)

        assert (
            str(exc_info.value.detail["title"])
            == ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO
        )
        assert (
            str(exc_info.value.detail["detail"])
            == ServicoErrorMessages.NOME_JA_CADASTRADO
        )
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_validation_error_com_message_dict_na_criacao(
        self,
    ) -> None:
        """Deve converter erros de validação organizados por campo."""
        view = self.criar_view_com_usuario()
        serializer = self.criar_serializer()
        erro = DjangoValidationError(
            {
                "nome": ["Nome inválido."],
            }
        )
        view.service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_create(serializer)

        mensagens = exc_info.value.detail["nome"]

        assert [str(mensagem) for mensagem in mensagens] == [
            "Nome inválido."
        ]
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_validation_error_com_messages_na_criacao(
        self,
    ) -> None:
        """Deve converter uma lista de mensagens de validação."""
        view = self.criar_view_com_usuario()
        serializer = self.criar_serializer()
        erro = DjangoValidationError(["Dados inválidos."])
        view.service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_create(serializer)

        assert [
            str(mensagem) for mensagem in exc_info.value.detail
        ] == ["Dados inválidos."]
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_erro_inesperado_na_criacao(
        self,
    ) -> None:
        """Deve converter erro inesperado em instabilidade."""
        view = self.criar_view_com_usuario()
        serializer = self.criar_serializer()
        erro = RuntimeError("Erro interno do banco")
        view.service.criar.side_effect = erro

        with pytest.raises(ServicoInstabilidadeError) as exc_info:
            view.perform_create(serializer)

        assert str(exc_info.value.detail["title"]) == "Erro"
        assert (
            str(exc_info.value.detail["detail"])
            == ServicoErrorMessages.INSTABILIDADE
        )
        assert exc_info.value.__cause__ is erro

    def test_deve_atualizar_servico_e_definir_instancia(
        self,
    ) -> None:
        """Deve delegar a atualização e definir a instância."""
        view = self.criar_view_com_usuario(usuario_id=20)
        servico_existente = Mock(spec=Servico)
        servico_atualizado = Mock(spec=Servico)
        serializer = self.criar_serializer(
            dados={
                "nome": "Pintura externa",
                "status": False,
            },
            instancia=servico_existente,
        )
        view.service.atualizar.return_value = servico_atualizado

        view.perform_update(serializer)

        view.service.atualizar.assert_called_once_with(
            servico=servico_existente,
            dados={
                "nome": "Pintura externa",
                "status": False,
            },
            usuario_id=20,
        )
        assert serializer.instance is servico_atualizado

    def test_deve_converter_erro_de_nome_duplicado_na_atualizacao(
        self,
    ) -> None:
        """Deve converter duplicidade em erro de validação."""
        view = self.criar_view_com_usuario()
        serializer = self.criar_serializer(
            instancia=Mock(spec=Servico),
        )
        erro = ServicoJaCadastradoError(
            title=ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO,
            detail=ServicoErrorMessages.NOME_JA_CADASTRADO,
        )
        view.service.atualizar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_update(serializer)

        assert (
            str(exc_info.value.detail["title"])
            == ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO
        )
        assert (
            str(exc_info.value.detail["detail"])
            == ServicoErrorMessages.NOME_JA_CADASTRADO
        )
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_validation_error_com_message_dict_na_atualizacao(
        self,
    ) -> None:
        """Deve converter erros de atualização organizados por campo."""
        view = self.criar_view_com_usuario()
        serializer = self.criar_serializer(
            instancia=Mock(spec=Servico),
        )
        erro = DjangoValidationError(
            {
                "nome": ["Nome inválido."],
            }
        )
        view.service.atualizar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_update(serializer)

        mensagens = exc_info.value.detail["nome"]

        assert [str(mensagem) for mensagem in mensagens] == [
            "Nome inválido."
        ]
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_validation_error_com_messages_na_atualizacao(
        self,
    ) -> None:
        """Deve converter uma lista de mensagens na atualização."""
        view = self.criar_view_com_usuario()
        serializer = self.criar_serializer(
            instancia=Mock(spec=Servico),
        )
        erro = DjangoValidationError(["Dados inválidos."])
        view.service.atualizar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_update(serializer)

        assert [
            str(mensagem) for mensagem in exc_info.value.detail
        ] == ["Dados inválidos."]
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_erro_inesperado_na_atualizacao(
        self,
    ) -> None:
        """Deve converter erro inesperado em instabilidade."""
        view = self.criar_view_com_usuario()
        serializer = self.criar_serializer(
            instancia=Mock(spec=Servico),
        )
        erro = RuntimeError("Erro interno do banco")
        view.service.atualizar.side_effect = erro

        with pytest.raises(ServicoInstabilidadeError) as exc_info:
            view.perform_update(serializer)

        assert str(exc_info.value.detail["title"]) == "Erro"
        assert (
            str(exc_info.value.detail["detail"])
            == ServicoErrorMessages.ERRO_AO_ATUALIZAR
        )
        assert exc_info.value.__cause__ is erro