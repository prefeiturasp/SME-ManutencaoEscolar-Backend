"""Testes das views DRF do domínio Serviço."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import (
    NotAuthenticated,
)
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer

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
            ServicoInstabilidadeError.default_code == "servico_instabilidade"
        )


class TestServicoViewSet:
    """Testa a view responsável pelo domínio Serviço."""

    @staticmethod
    def criar_view_com_usuario(
        usuario_id: int | None = 10,
    ) -> tuple[ServicoViewSet, Mock]:
        """Cria uma view com usuário e service simulados."""
        view = ServicoViewSet()

        request = Mock()
        request.user.pk = usuario_id
        view.request = cast(Request, request)

        service = Mock(spec=ServicoService)
        view.service = cast(ServicoService, service)

        return view, service

    @staticmethod
    def criar_serializer(
        dados: dict[str, Any] | None = None,
        instancia: Servico | None = None,
    ) -> BaseSerializer[Any]:
        """Cria um serializer simulado para os testes da view."""
        serializer = Mock()
        serializer.validated_data = dados if dados is not None else {}
        serializer.instance = instancia

        return cast(BaseSerializer[Any], serializer)

    @staticmethod
    def criar_servico(
        nome: str = "Pintura",
        status_servico: bool = True,
    ) -> Servico:
        """Cria uma instância não persistida de Serviço."""
        return Servico(
            nome=nome,
            status=status_servico,
        )

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

    def test_deve_retornar_id_do_usuario(self) -> None:
        """Deve retornar o ID do usuário autenticado."""
        view, _service = self.criar_view_com_usuario(usuario_id=25)

        resultado = view._obter_usuario_id()

        assert resultado == 25

    def test_deve_rejeitar_usuario_sem_id(self) -> None:
        """Deve rejeitar um usuário que não possua ID."""
        view, _service = self.criar_view_com_usuario(usuario_id=None)

        with pytest.raises(NotAuthenticated) as exc_info:
            view._obter_usuario_id()

        assert str(exc_info.value.detail) == ("Usuário não identificado.")

    def test_deve_retornar_servico_do_serializer(self) -> None:
        """Deve retornar a instância válida do serializer."""
        servico = self.criar_servico()
        serializer = self.criar_serializer(instancia=servico)

        resultado = ServicoViewSet._obter_servico(serializer)

        assert resultado is servico

    @pytest.mark.parametrize(
        "instancia",
        [
            None,
            "serviço inválido",
            object(),
        ],
    )
    def test_deve_rejeitar_instancia_de_servico_invalida(
        self,
        instancia: object | None,
    ) -> None:
        """Deve rejeitar uma instância que não seja Serviço."""
        serializer = self.criar_serializer()
        serializer.instance = instancia

        with pytest.raises(DRFValidationError) as exc_info:
            ServicoViewSet._obter_servico(serializer)

        assert str(exc_info.value.detail["title"]) == "Erro"
        assert str(exc_info.value.detail["detail"]) == (
            "Serviço inválido ou não encontrado."
        )

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
        serializer_esperado: type[BaseSerializer[Any]],
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
        view, service = self.criar_view_com_usuario(usuario_id=10)
        dados = {
            "nome": "Pintura",
            "status": True,
        }
        serializer = self.criar_serializer(dados=dados)
        servico_criado = self.criar_servico()

        service.criar.return_value = servico_criado

        view.perform_create(serializer)

        service.criar.assert_called_once_with(
            dados,
            usuario_id=10,
        )
        assert serializer.instance is servico_criado

    def test_deve_converter_erro_de_nome_duplicado_na_criacao(
        self,
    ) -> None:
        """Deve converter duplicidade em erro de validação."""
        view, service = self.criar_view_com_usuario()
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
        service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_create(serializer)

        assert str(exc_info.value.detail["title"]) == (
            ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO
        )
        assert str(exc_info.value.detail["detail"]) == (
            ServicoErrorMessages.NOME_JA_CADASTRADO
        )
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_message_dict_na_criacao(
        self,
    ) -> None:
        """Deve converter erros organizados por campo na criação."""
        view, service = self.criar_view_com_usuario()
        serializer = self.criar_serializer()
        erro = DjangoValidationError(
            {
                "nome": ["Nome inválido."],
            }
        )
        service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_create(serializer)

        mensagens = exc_info.value.detail["nome"]

        assert [str(mensagem) for mensagem in mensagens] == ["Nome inválido."]
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_messages_na_criacao(
        self,
    ) -> None:
        """Deve converter uma lista de mensagens na criação."""
        view, service = self.criar_view_com_usuario()
        serializer = self.criar_serializer()
        erro = DjangoValidationError(["Dados inválidos."])
        service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_create(serializer)

        assert [str(mensagem) for mensagem in exc_info.value.detail] == [
            "Dados inválidos."
        ]
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_erro_inesperado_na_criacao(
        self,
    ) -> None:
        """Deve converter erro inesperado em instabilidade."""
        view, service = self.criar_view_com_usuario()
        serializer = self.criar_serializer()
        erro = RuntimeError("Erro interno do banco")
        service.criar.side_effect = erro

        with pytest.raises(ServicoInstabilidadeError) as exc_info:
            view.perform_create(serializer)

        assert exc_info.value.status_code == 500
        assert str(exc_info.value.detail["title"]) == "Erro"
        assert str(exc_info.value.detail["detail"]) == (
            ServicoErrorMessages.INSTABILIDADE
        )
        assert exc_info.value.__cause__ is erro

    def test_deve_atualizar_servico_e_definir_instancia(
        self,
    ) -> None:
        """Deve delegar a atualização e definir a instância."""
        view, service = self.criar_view_com_usuario(usuario_id=20)
        servico_existente = self.criar_servico()
        servico_atualizado = self.criar_servico(
            nome="Pintura externa",
            status_servico=False,
        )
        dados = {
            "nome": "Pintura externa",
            "status": False,
        }
        serializer = self.criar_serializer(
            dados=dados,
            instancia=servico_existente,
        )
        service.atualizar.return_value = servico_atualizado

        view.perform_update(serializer)

        service.atualizar.assert_called_once_with(
            servico=servico_existente,
            dados=dados,
            usuario_id=20,
        )
        assert serializer.instance is servico_atualizado

    def test_deve_converter_erro_de_nome_duplicado_na_atualizacao(
        self,
    ) -> None:
        """Deve converter duplicidade em erro de validação."""
        view, service = self.criar_view_com_usuario()
        serializer = self.criar_serializer(
            instancia=self.criar_servico(),
        )
        erro = ServicoJaCadastradoError(
            title=ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO,
            detail=ServicoErrorMessages.NOME_JA_CADASTRADO,
        )
        service.atualizar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_update(serializer)

        assert str(exc_info.value.detail["title"]) == (
            ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO
        )
        assert str(exc_info.value.detail["detail"]) == (
            ServicoErrorMessages.NOME_JA_CADASTRADO
        )
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_message_dict_na_atualizacao(
        self,
    ) -> None:
        """Deve converter erros organizados por campo na atualização."""
        view, service = self.criar_view_com_usuario()
        serializer = self.criar_serializer(
            instancia=self.criar_servico(),
        )
        erro = DjangoValidationError(
            {
                "nome": ["Nome inválido."],
            }
        )
        service.atualizar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_update(serializer)

        mensagens = exc_info.value.detail["nome"]

        assert [str(mensagem) for mensagem in mensagens] == ["Nome inválido."]
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_messages_na_atualizacao(
        self,
    ) -> None:
        """Deve converter uma lista de mensagens na atualização."""
        view, service = self.criar_view_com_usuario()
        serializer = self.criar_serializer(
            instancia=self.criar_servico(),
        )
        erro = DjangoValidationError(["Dados inválidos."])
        service.atualizar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_update(serializer)

        assert [str(mensagem) for mensagem in exc_info.value.detail] == [
            "Dados inválidos."
        ]
        assert exc_info.value.__cause__ is erro

    def test_deve_converter_erro_inesperado_na_atualizacao(
        self,
    ) -> None:
        """Deve converter erro inesperado em instabilidade."""
        view, service = self.criar_view_com_usuario()
        serializer = self.criar_serializer(
            instancia=self.criar_servico(),
        )
        erro = RuntimeError("Erro interno do banco")
        service.atualizar.side_effect = erro

        with pytest.raises(ServicoInstabilidadeError) as exc_info:
            view.perform_update(serializer)

        assert exc_info.value.status_code == 500
        assert str(exc_info.value.detail["title"]) == "Erro"
        assert str(exc_info.value.detail["detail"]) == (
            ServicoErrorMessages.ERRO_AO_ATUALIZAR
        )
        assert exc_info.value.__cause__ is erro
