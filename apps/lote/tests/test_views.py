"""Testes das views DRF do domínio de lotes."""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import (
    NotAuthenticated,
)
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer

from apps.core.pagination import PaginacaoPadrao
from apps.lote.api.views import (
    LoteInstabilidadeError,
    LoteViewSet,
)
from apps.lote.constants import LoteErrorMessages
from apps.lote.exceptions import DiretoriaRegionalJaVinculadaError
from apps.lote.filters import LoteFilter
from apps.lote.models import Lote
from apps.lote.serializers import (
    LoteCriarSerializer,
    LoteSerializer,
)
from apps.lote.services.lote_service import LoteService
from apps.usuarios.models.usuario import Usuario


class TestLoteInstabilidadeError:
    """Testa a exceção de instabilidade de lotes."""

    def test_deve_possuir_configuracao_esperada(self) -> None:
        """Deve possuir status, mensagem e código esperados."""
        assert (
            LoteInstabilidadeError.status_code
            == status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        assert (
            LoteInstabilidadeError.default_detail
            == LoteErrorMessages.INSTABILIDADE
        )
        assert LoteInstabilidadeError.default_code == "lote_instabilidade"

    def test_deve_aceitar_detail_personalizado(self) -> None:
        """Deve permitir a criação com detalhes personalizados."""
        erro = LoteInstabilidadeError(
            {
                "title": "Erro",
                "detail": LoteErrorMessages.INSTABILIDADE,
            }
        )

        assert erro.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert str(erro.detail["title"]) == "Erro"
        assert str(erro.detail["detail"]) == (LoteErrorMessages.INSTABILIDADE)


class TestLoteViewSet:
    """Testa a view responsável pelo domínio de lotes."""

    @staticmethod
    def criar_view(
        usuario: object | None = None,
    ) -> tuple[LoteViewSet, Mock]:
        """Cria uma view com usuário e service simulados."""
        view = LoteViewSet()

        if usuario is None:
            usuario = Usuario()

        view.request = cast(
            Request,
            SimpleNamespace(user=usuario),
        )

        service = Mock(spec=LoteService)
        view.service = cast(LoteService, service)

        return view, service

    @staticmethod
    def criar_serializer(
        dados: dict[str, Any] | None = None,
        instancia: object | None = None,
    ) -> tuple[BaseSerializer, Mock]:
        """Cria um serializer simulado."""
        serializer_mock = Mock(spec=BaseSerializer)
        serializer_mock.validated_data = dados if dados is not None else {}
        serializer_mock.instance = instancia

        return (
            cast(BaseSerializer, serializer_mock),
            serializer_mock,
        )

    @staticmethod
    def criar_lote(
        nome: str = "Lote Centro",
        codigo_cadastro: str = "LOTE-001",
    ) -> Lote:
        """Cria uma instância não persistida de lote."""
        return Lote(
            nome=nome,
            codigo_cadastro=codigo_cadastro,
        )

    @staticmethod
    def criar_erro_diretoria_vinculada() -> DiretoriaRegionalJaVinculadaError:
        """Cria um erro de diretoria já vinculada."""
        return DiretoriaRegionalJaVinculadaError(
            title="Diretoria Regional já vinculada",
            detail={
                "message": (LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA),
                "vinculados": [
                    (
                        "Diretoria Regional Centro",
                        "LOTE-002",
                    )
                ],
            },
        )

    @patch("apps.lote.api.views.LoteService")
    def test_deve_criar_service_ao_instanciar_view(
        self,
        mock_service_class: Mock,
    ) -> None:
        """Deve criar o service utilizado pela view."""
        service = mock_service_class.return_value

        view = LoteViewSet()

        assert view.service is service
        mock_service_class.assert_called_once_with()

    def test_deve_possuir_configuracoes_da_view(self) -> None:
        """Deve possuir as configurações esperadas."""
        view = LoteViewSet()

        assert view.http_method_names == [
            "get",
            "post",
            "patch",
            "options",
            "delete",
        ]
        assert view.lookup_field == "uuid"
        assert view.filter_backends == [DjangoFilterBackend]
        assert view.filterset_class is LoteFilter
        assert view.pagination_class is PaginacaoPadrao

    def test_deve_retornar_usuario_autenticado(self) -> None:
        """Deve retornar o usuário autenticado."""
        usuario = Usuario()
        view, _service = self.criar_view(usuario)

        resultado = view._obter_usuario()

        assert resultado is usuario

    @pytest.mark.parametrize(
        "usuario",
        [
            None,
            object(),
            "usuário inválido",
            SimpleNamespace(pk=10),
        ],
    )
    def test_deve_rejeitar_usuario_invalido(
        self,
        usuario: object | None,
    ) -> None:
        """Deve rejeitar usuário que não seja uma instância válida."""
        view, _service = self.criar_view(Usuario())
        view.request = cast(
            Request,
            SimpleNamespace(user=usuario),
        )

        with pytest.raises(NotAuthenticated) as exc_info:
            view._obter_usuario()

        assert str(exc_info.value.detail) == ("Usuário não identificado.")

    def test_deve_retornar_lote_do_serializer(self) -> None:
        """Deve retornar a instância válida do serializer."""
        lote = self.criar_lote()
        serializer, _serializer_mock = self.criar_serializer(
            instancia=lote,
        )

        resultado = LoteViewSet._obter_lote(serializer)

        assert resultado is lote

    @pytest.mark.parametrize(
        "instancia",
        [
            None,
            object(),
            "lote inválido",
            SimpleNamespace(uuid="uuid-lote"),
        ],
    )
    def test_deve_rejeitar_instancia_de_lote_invalida(
        self,
        instancia: object | None,
    ) -> None:
        """Deve rejeitar uma instância que não seja Lote."""
        serializer, _serializer_mock = self.criar_serializer(
            instancia=instancia,
        )

        with pytest.raises(DRFValidationError) as exc_info:
            LoteViewSet._obter_lote(serializer)

        assert str(exc_info.value.detail["title"]) == "Erro"
        assert str(exc_info.value.detail["detail"]) == (
            "Lote inválido ou não encontrado."
        )

    @pytest.mark.parametrize(
        "acao",
        [
            "create",
            "partial_update",
        ],
    )
    def test_deve_retornar_serializer_de_escrita(
        self,
        acao: str,
    ) -> None:
        """Deve usar o serializer de escrita nas alterações."""
        view = LoteViewSet()
        view.action = acao

        resultado = view.get_serializer_class()

        assert resultado is LoteCriarSerializer

    @pytest.mark.parametrize(
        "acao",
        [
            "list",
            "retrieve",
            "destroy",
            "update",
        ],
    )
    def test_deve_retornar_serializer_de_leitura(
        self,
        acao: str,
    ) -> None:
        """Deve usar o serializer de leitura nas demais ações."""
        view = LoteViewSet()
        view.action = acao

        resultado = view.get_serializer_class()

        assert resultado is LoteSerializer

    def test_deve_criar_lote_e_definir_instancia(
        self,
    ) -> None:
        """Deve delegar a criação e definir a instância criada."""
        usuario = Usuario()
        view, service = self.criar_view(usuario)

        dados: dict[str, Any] = {
            "nome": "Lote Centro",
            "codigo_cadastro": "LOTE-001",
        }
        serializer, serializer_mock = self.criar_serializer(
            dados=dados,
        )
        lote_criado = self.criar_lote()

        service.criar.return_value = lote_criado

        view.perform_create(serializer)

        service.criar.assert_called_once_with(
            dados=dados,
            usuario=usuario,
        )
        assert serializer_mock.instance is lote_criado

    def test_deve_converter_diretoria_vinculada_na_criacao(
        self,
    ) -> None:
        """Deve converter conflito de diretoria durante a criação."""
        view, service = self.criar_view()
        serializer, serializer_mock = self.criar_serializer()
        erro = self.criar_erro_diretoria_vinculada()

        service.criar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_create(serializer)

        assert str(exc_info.value.detail["title"]) == erro.title
        assert "detail" in exc_info.value.detail
        assert serializer_mock.instance is None

    def test_deve_converter_validation_error_por_campo_na_criacao(
        self,
    ) -> None:
        """Deve converter validação por campo durante a criação."""
        view, service = self.criar_view()
        serializer, serializer_mock = self.criar_serializer()

        service.criar.side_effect = DjangoValidationError(
            {
                "nome": [
                    "Este campo é obrigatório.",
                ]
            }
        )

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_create(serializer)

        assert str(exc_info.value.detail["nome"][0]) == (
            "Este campo é obrigatório."
        )
        assert serializer_mock.instance is None

    def test_deve_converter_validation_error_geral_na_criacao(
        self,
    ) -> None:
        """Deve converter validação geral durante a criação."""
        view, service = self.criar_view()
        serializer, serializer_mock = self.criar_serializer()

        service.criar.side_effect = DjangoValidationError("Dados inválidos.")

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_create(serializer)

        assert str(exc_info.value.detail[0]) == "Dados inválidos."
        assert serializer_mock.instance is None

    def test_deve_converter_erro_inesperado_na_criacao(
        self,
    ) -> None:
        """Deve converter erro inesperado em instabilidade."""
        view, service = self.criar_view()
        serializer, serializer_mock = self.criar_serializer()

        service.criar.side_effect = RuntimeError("Erro inesperado.")

        with pytest.raises(LoteInstabilidadeError) as exc_info:
            view.perform_create(serializer)

        assert (
            exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        assert str(exc_info.value.detail["title"]) == "Erro"
        assert str(exc_info.value.detail["detail"]) == (
            LoteErrorMessages.INSTABILIDADE
        )
        assert serializer_mock.instance is None

    def test_deve_atualizar_lote_e_manter_instancia(
        self,
    ) -> None:
        """Deve delegar a atualização ao service."""
        usuario = Usuario()
        lote = self.criar_lote()
        view, service = self.criar_view(usuario)

        dados: dict[str, Any] = {
            "nome": "Lote atualizado",
        }
        serializer, serializer_mock = self.criar_serializer(
            dados=dados,
            instancia=lote,
        )

        view.perform_update(serializer)

        service.atualizar.assert_called_once_with(
            lote=lote,
            dados=dados,
            usuario=usuario,
        )
        assert serializer_mock.instance is lote

    def test_deve_converter_diretoria_vinculada_na_atualizacao(
        self,
    ) -> None:
        """Deve converter conflito de diretoria na atualização."""
        lote = self.criar_lote()
        view, service = self.criar_view()
        serializer, serializer_mock = self.criar_serializer(
            instancia=lote,
        )
        erro = self.criar_erro_diretoria_vinculada()

        service.atualizar.side_effect = erro

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_update(serializer)

        assert str(exc_info.value.detail["title"]) == erro.title
        assert "detail" in exc_info.value.detail
        assert serializer_mock.instance is lote

    def test_deve_converter_validation_error_por_campo_na_atualizacao(
        self,
    ) -> None:
        """Deve converter validação por campo na atualização."""
        lote = self.criar_lote()
        view, service = self.criar_view()
        serializer, serializer_mock = self.criar_serializer(
            instancia=lote,
        )

        service.atualizar.side_effect = DjangoValidationError(
            {
                "nome": [
                    "Já existe um lote com este nome.",
                ]
            }
        )

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_update(serializer)

        assert str(exc_info.value.detail["nome"][0]) == (
            "Já existe um lote com este nome."
        )
        assert serializer_mock.instance is lote

    def test_deve_converter_validation_error_geral_na_atualizacao(
        self,
    ) -> None:
        """Deve converter validação geral na atualização."""
        lote = self.criar_lote()
        view, service = self.criar_view()
        serializer, serializer_mock = self.criar_serializer(
            instancia=lote,
        )

        service.atualizar.side_effect = DjangoValidationError(
            "Dados inválidos."
        )

        with pytest.raises(DRFValidationError) as exc_info:
            view.perform_update(serializer)

        assert str(exc_info.value.detail[0]) == "Dados inválidos."
        assert serializer_mock.instance is lote

    def test_deve_converter_erro_inesperado_na_atualizacao(
        self,
    ) -> None:
        """Deve converter erro inesperado em instabilidade."""
        lote = self.criar_lote()
        view, service = self.criar_view()
        serializer, serializer_mock = self.criar_serializer(
            instancia=lote,
        )

        service.atualizar.side_effect = RuntimeError("Erro inesperado.")

        with pytest.raises(LoteInstabilidadeError) as exc_info:
            view.perform_update(serializer)

        assert (
            exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        assert str(exc_info.value.detail["title"]) == "Erro"
        assert str(exc_info.value.detail["detail"]) == (
            LoteErrorMessages.INSTABILIDADE
        )
        assert serializer_mock.instance is lote

    def test_deve_deletar_lote_com_usuario_autenticado(
        self,
    ) -> None:
        """Deve delegar a exclusão do lote ao service."""
        usuario = Usuario()
        lote = self.criar_lote()
        view, service = self.criar_view(usuario)

        view.perform_destroy(lote)

        service.deletar.assert_called_once_with(
            lote,
            usuario,
        )

    def test_deve_rejeitar_exclusao_sem_usuario_valido(
        self,
    ) -> None:
        """Não deve excluir quando o usuário não for válido."""
        lote = self.criar_lote()
        view, service = self.criar_view()
        view.request = cast(
            Request,
            SimpleNamespace(user=None),
        )

        with pytest.raises(NotAuthenticated) as exc_info:
            view.perform_destroy(lote)

        assert str(exc_info.value.detail) == ("Usuário não identificado.")
        service.deletar.assert_not_called()
