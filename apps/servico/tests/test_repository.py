"""Testes para o repositório de Serviço."""

from typing import Any
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from apps.servico.models import Servico
from apps.servico.repository.servico_repository import ServicoRepository


class TestServicoRepository:
    """Testa as operações de persistência de serviços."""

    def test_deve_utilizar_model_servico(self) -> None:
        """Deve utilizar o model Serviço nas operações."""
        repository = ServicoRepository()

        assert repository.model is Servico

    @pytest.mark.parametrize("resultado_esperado", [True, False])
    def test_deve_verificar_se_servico_existe_por_nome(
        self,
        resultado_esperado: bool,
    ) -> None:
        """Deve consultar o serviço pelo nome sem excluir UUID."""
        repository = ServicoRepository()
        queryset = Mock()
        queryset.exists.return_value = resultado_esperado

        with patch.object(
            Servico.objects,
            "filter",
            return_value=queryset,
        ) as mock_filter:
            resultado = repository.existe_por_nome("Pintura")

        mock_filter.assert_called_once_with(nome__iexact="Pintura")
        queryset.exclude.assert_not_called()
        queryset.exists.assert_called_once_with()

        assert resultado is resultado_esperado

    def test_deve_excluir_uuid_ao_verificar_nome(
        self,
    ) -> None:
        """Deve desconsiderar o serviço identificado pelo UUID."""
        repository = ServicoRepository()
        servico_uuid = uuid4()

        queryset = Mock()
        queryset_sem_servico_atual = Mock()
        queryset.exclude.return_value = queryset_sem_servico_atual
        queryset_sem_servico_atual.exists.return_value = False

        with patch.object(
            Servico.objects,
            "filter",
            return_value=queryset,
        ) as mock_filter:
            resultado = repository.existe_por_nome(
                "Pintura",
                excluir_uuid=servico_uuid,
            )

        mock_filter.assert_called_once_with(nome__iexact="Pintura")
        queryset.exclude.assert_called_once_with(uuid=servico_uuid)
        queryset_sem_servico_atual.exists.assert_called_once_with()

        assert resultado is False

    def test_deve_criar_validar_salvar_e_retornar_servico(
        self,
        servico_payload_valido: dict[str, Any],
    ) -> None:
        """Deve criar, validar, salvar e retornar o serviço."""
        repository = ServicoRepository()
        usuario_id = 10

        with (
            patch.object(
                Servico,
                "full_clean",
                autospec=True,
            ) as mock_full_clean,
            patch.object(
                Servico,
                "save",
                autospec=True,
            ) as mock_save,
        ):
            resultado = repository.criar(
                dados=servico_payload_valido,
                usuario_id=usuario_id,
            )

        mock_full_clean.assert_called_once_with(resultado)
        mock_save.assert_called_once_with(resultado)

        assert isinstance(resultado, Servico)
        assert resultado.nome == servico_payload_valido["nome"]
        assert resultado.status == servico_payload_valido["status"]
        assert resultado.criado_por_id == usuario_id
        assert resultado.atualizado_por_id == usuario_id

    def test_deve_atualizar_todos_os_campos(
        self,
    ) -> None:
        """Deve atualizar nome, status e usuário atualizador."""
        repository = ServicoRepository()
        servico = Servico(
            nome="Pintura",
            status=True,
        )
        usuario_id = 20

        dados = {
            "nome": "Pintura externa",
            "status": False,
        }

        with (
            patch.object(
                servico,
                "full_clean",
            ) as mock_full_clean,
            patch.object(
                servico,
                "save",
            ) as mock_save,
        ):
            resultado = repository.atualizar(
                servico=servico,
                dados=dados,
                usuario_id=usuario_id,
            )

        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once_with()

        assert resultado is servico
        assert resultado.nome == "Pintura externa"
        assert resultado.status is False
        assert resultado.atualizado_por_id == usuario_id

    def test_deve_manter_campos_nao_informados(
        self,
    ) -> None:
        """Deve preservar nome e status quando não forem enviados."""
        repository = ServicoRepository()
        servico = Servico(
            nome="Pintura",
            status=True,
        )
        usuario_id = 30

        with (
            patch.object(
                servico,
                "full_clean",
            ) as mock_full_clean,
            patch.object(
                servico,
                "save",
            ) as mock_save,
        ):
            resultado = repository.atualizar(
                servico=servico,
                dados={},
                usuario_id=usuario_id,
            )

        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once_with()

        assert resultado is servico
        assert resultado.nome == "Pintura"
        assert resultado.status is True
        assert resultado.atualizado_por_id == usuario_id