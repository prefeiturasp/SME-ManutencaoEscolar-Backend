"""Testes do serviço de domínio Serviço."""

from typing import cast
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.models import Servico
from apps.servico.repository.servico_repository import ServicoRepository
from apps.servico.services.servico_service import ServicoService
from apps.usuarios.models.usuario import Usuario


class TestServicoService:
    """Testa as regras de negócio de ServicoService."""

    @staticmethod
    def criar_usuario(usuario_id: int = 10) -> Usuario:
        """Cria um usuário simulado para os testes."""
        usuario = Mock(spec=Usuario)
        usuario.pk = usuario_id

        return cast(Usuario, usuario)

    def test_deve_utilizar_repository_informado(self) -> None:
        """Deve armazenar o repositório recebido."""
        repository = Mock(spec=ServicoRepository)

        service = ServicoService(repository=repository)

        assert service.repository is repository

    @patch("apps.servico.services.servico_service.ServicoRepository")
    def test_deve_criar_repository_padrao(
        self,
        mock_repository_class: Mock,
    ) -> None:
        """Deve criar o repositório padrão quando não for informado."""
        repository = mock_repository_class.return_value

        service = ServicoService()

        assert service.repository is repository
        mock_repository_class.assert_called_once_with()

    def test_deve_normalizar_nome_e_criar_servico(self) -> None:
        """Deve normalizar o nome e delegar a criação ao repository."""
        repository = Mock(spec=ServicoRepository)
        servico_criado = Mock(spec=Servico)
        usuario = self.criar_usuario(usuario_id=10)

        repository.existe_por_nome.return_value = False
        repository.criar.return_value = servico_criado

        service = ServicoService(repository=repository)
        dados = {
            "nome": "  Pintura  ",
            "status": True,
        }

        resultado = service.criar(
            dados,
            usuario=usuario,
        )

        repository.existe_por_nome.assert_called_once_with("Pintura")
        repository.criar.assert_called_once_with(
            {
                "nome": "Pintura",
                "status": True,
            },
            usuario=usuario,
        )

        assert resultado is servico_criado
        assert dados == {
            "nome": "  Pintura  ",
            "status": True,
        }

    def test_deve_lancar_erro_ao_criar_nome_duplicado(self) -> None:
        """Não deve criar um serviço quando o nome já existir."""
        repository = Mock(spec=ServicoRepository)
        usuario = self.criar_usuario(usuario_id=10)
        repository.existe_por_nome.return_value = True

        service = ServicoService(repository=repository)
        dados = {
            "nome": "  Pintura  ",
            "status": True,
        }

        with pytest.raises(ServicoJaCadastradoError) as exc_info:
            service.criar(
                dados,
                usuario=usuario,
            )

        assert (
            exc_info.value.title
            == ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO
        )
        assert exc_info.value.detail == ServicoErrorMessages.NOME_JA_CADASTRADO

        repository.existe_por_nome.assert_called_once_with("Pintura")
        repository.criar.assert_not_called()

        assert dados["nome"] == "  Pintura  "

    def test_deve_normalizar_nome_e_atualizar_servico(self) -> None:
        """Deve normalizar o nome e delegar a atualização."""
        repository = Mock(spec=ServicoRepository)
        usuario = self.criar_usuario(usuario_id=20)
        servico_existente = Mock(spec=Servico)
        servico_atualizado = Mock(spec=Servico)
        servico_existente.uuid = uuid4()

        repository.existe_por_nome.return_value = False
        repository.atualizar.return_value = servico_atualizado

        service = ServicoService(repository=repository)
        dados = {
            "nome": "  Pintura externa  ",
            "status": False,
        }

        resultado = service.atualizar(
            servico=servico_existente,
            dados=dados,
            usuario=usuario,
        )

        repository.existe_por_nome.assert_called_once_with(
            "Pintura externa",
            excluir_uuid=servico_existente.uuid,
        )
        repository.atualizar.assert_called_once_with(
            servico_existente,
            {
                "nome": "Pintura externa",
                "status": False,
            },
            usuario=usuario,
        )

        assert resultado is servico_atualizado
        assert dados == {
            "nome": "  Pintura externa  ",
            "status": False,
        }

    def test_deve_atualizar_servico_sem_nome(self) -> None:
        """Deve atualizar os demais campos quando o nome não for enviado."""
        repository = Mock(spec=ServicoRepository)
        usuario = self.criar_usuario(usuario_id=20)
        servico_existente = Mock(spec=Servico)
        servico_atualizado = Mock(spec=Servico)

        repository.atualizar.return_value = servico_atualizado

        service = ServicoService(repository=repository)
        dados = {
            "status": False,
        }

        resultado = service.atualizar(
            servico=servico_existente,
            dados=dados,
            usuario=usuario,
        )

        repository.existe_por_nome.assert_not_called()
        repository.atualizar.assert_called_once_with(
            servico_existente,
            {
                "status": False,
            },
            usuario=usuario,
        )

        assert resultado is servico_atualizado
        assert dados == {"status": False}

    def test_deve_lancar_erro_ao_atualizar_nome_duplicado(
        self,
    ) -> None:
        """Não deve atualizar quando o nome pertencer a outro serviço."""
        repository = Mock(spec=ServicoRepository)
        usuario = self.criar_usuario(usuario_id=20)
        servico_existente = Mock(spec=Servico)
        servico_existente.uuid = uuid4()
        repository.existe_por_nome.return_value = True

        service = ServicoService(repository=repository)
        dados = {
            "nome": "  Elétrica  ",
            "status": True,
        }

        with pytest.raises(ServicoJaCadastradoError) as exc_info:
            service.atualizar(
                servico=servico_existente,
                dados=dados,
                usuario=usuario,
            )

        assert (
            exc_info.value.title
            == ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO
        )
        assert exc_info.value.detail == ServicoErrorMessages.NOME_JA_CADASTRADO

        repository.existe_por_nome.assert_called_once_with(
            "Elétrica",
            excluir_uuid=servico_existente.uuid,
        )
        repository.atualizar.assert_not_called()

        assert dados["nome"] == "  Elétrica  "

    def test_deve_delegar_exclusao_logica_ao_repository(self) -> None:
        """Deve delegar a exclusão lógica ao repository."""
        repository = Mock(spec=ServicoRepository)
        usuario = self.criar_usuario(usuario_id=30)
        servico = Mock(spec=Servico)
        resultado_esperado = (
            1,
            {
                "servico.Servico": 1,
            },
        )
        repository.deletar.return_value = resultado_esperado

        service = ServicoService(repository=repository)

        resultado = service.deletar(
            model_servico=servico,
            usuario=usuario,
        )

        repository.deletar.assert_called_once_with(
            usuario,
            servico,
        )
        assert resultado == resultado_esperado
