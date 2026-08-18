"""Testes para o repositório de Serviço."""

from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest

from apps.servico.models import Servico
from apps.servico.repository.servico_repository import ServicoRepository
from apps.usuarios.models.usuario import Usuario


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
        """Deve consultar serviços ativos pelo nome."""
        repository = ServicoRepository()
        queryset_mock = patch.object(
            Servico.objects,
            "filter",
        )

        with queryset_mock as mock_filter:
            queryset_filtrado = mock_filter.return_value
            queryset_filtrado.exists.return_value = resultado_esperado

            resultado = repository.existe_por_nome("Pintura")

        mock_filter.assert_called_once_with(
            nome__iexact="Pintura",
            deletado_em__isnull=True,
        )
        queryset_filtrado.exclude.assert_not_called()
        queryset_filtrado.exists.assert_called_once_with()

        assert resultado is resultado_esperado

    def test_deve_excluir_uuid_ao_verificar_nome(self) -> None:
        """Deve desconsiderar o serviço identificado pelo UUID."""
        repository = ServicoRepository()
        servico_uuid = uuid4()

        with patch.object(
            Servico.objects,
            "filter",
        ) as mock_filter:
            queryset_filtrado = mock_filter.return_value
            queryset_sem_servico = queryset_filtrado.exclude.return_value
            queryset_sem_servico.exists.return_value = False

            resultado = repository.existe_por_nome(
                "Pintura",
                excluir_uuid=servico_uuid,
            )

        mock_filter.assert_called_once_with(
            nome__iexact="Pintura",
            deletado_em__isnull=True,
        )
        queryset_filtrado.exclude.assert_called_once_with(
            uuid=servico_uuid,
        )
        queryset_sem_servico.exists.assert_called_once_with()

        assert resultado is False

    def test_deve_criar_validar_salvar_e_retornar_servico(
        self,
        servico_payload_valido: dict[str, Any],
    ) -> None:
        """Deve criar, validar, salvar e retornar os dados do serviço."""
        repository = ServicoRepository()
        usuario = Usuario(id=10)

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
                usuario=usuario,
            )

        servico_criado = mock_full_clean.call_args.args[0]

        mock_full_clean.assert_called_once_with(servico_criado)
        mock_save.assert_called_once_with(servico_criado)

        assert isinstance(resultado, dict)
        assert resultado["id"] is servico_criado.id
        assert resultado["uuid"] == str(servico_criado.uuid)
        assert resultado["nome"] == servico_payload_valido["nome"]
        assert resultado["status"] == servico_payload_valido["status"]

        assert servico_criado.criado_por is usuario
        assert servico_criado.atualizado_por is usuario
        assert servico_criado.criado_por_id == usuario.id
        assert servico_criado.atualizado_por_id == usuario.id

    def test_deve_atualizar_todos_os_campos(self) -> None:
        """Deve atualizar nome, status e usuário atualizador."""
        repository = ServicoRepository()
        usuario = Usuario(id=20)
        servico = Servico(
            nome="Pintura",
            status=True,
        )
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
                usuario=usuario,
            )

        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once_with()

        assert isinstance(resultado, dict)
        assert resultado["nome"] == "Pintura externa"
        assert resultado["status"] is False
        assert resultado["atualizado_por"] == usuario.id

        assert servico.nome == "Pintura externa"
        assert servico.status is False
        assert servico.atualizado_por is usuario
        assert servico.atualizado_por_id == usuario.id

    def test_deve_manter_campos_nao_informados(self) -> None:
        """Deve preservar nome e status quando não forem enviados."""
        repository = ServicoRepository()
        usuario = Usuario(id=30)
        servico = Servico(
            nome="Pintura",
            status=True,
        )

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
                usuario=usuario,
            )

        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once_with()

        assert isinstance(resultado, dict)
        assert resultado["nome"] == "Pintura"
        assert resultado["status"] is True
        assert resultado["atualizado_por"] == usuario.id

        assert servico.nome == "Pintura"
        assert servico.status is True
        assert servico.atualizado_por is usuario
        assert servico.atualizado_por_id == usuario.id

    def test_deve_realizar_exclusao_logica(self) -> None:
        """Deve registrar o usuário e executar a exclusão lógica."""
        repository = ServicoRepository()
        usuario = Usuario(id=40)
        servico = Servico(
            nome="Pintura",
            status=True,
        )

        with (
            patch.object(
                servico,
                "save",
            ) as mock_save,
            patch.object(
                servico,
                "soft_delete",
            ) as mock_soft_delete,
        ):
            repository.deletar(
                usuario=usuario,
                model_servico=servico,
            )

        assert servico.deletado_por is usuario
        assert servico.deletado_por_id == usuario.id

        mock_save.assert_called_once_with(
            update_fields=["deletado_por"],
        )
        mock_soft_delete.assert_called_once_with(
            usuario=usuario,
        )
