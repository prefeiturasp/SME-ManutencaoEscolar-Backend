"""Testes do serviço de domínio Serviço."""

from unittest.mock import Mock, patch

import pytest

from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.repository.servico_repository import ServicoRepository
from apps.servico.services.servico_service import ServicoService


class TestServicoService:
    """Testes para ServicoService."""

    def test_deve_utilizar_repository_informado(self):
        """Deve armazenar o repositório recebido."""
        repository = Mock(spec=ServicoRepository)

        service = ServicoService(repository=repository)

        assert service.repository is repository

    @patch("apps.servico.services.servico_service.ServicoRepository")
    def test_deve_criar_repository_padrao(
        self,
        mock_repository_class,
    ):
        """Deve criar o repositório padrão quando não informado."""
        repository = mock_repository_class.return_value

        service = ServicoService()

        assert service.repository is repository
        mock_repository_class.assert_called_once_with()

    def test_deve_normalizar_nome_e_criar_servico(self):
        """Deve retirar espaços do nome antes da criação."""
        repository = Mock(spec=ServicoRepository)
        repository.existe_por_nome.return_value = False
        repository.criar.return_value = {
            "nome": "Pintura",
            "status": True,
        }

        service = ServicoService(repository)
        dados = {
            "nome": "  Pintura  ",
            "status": True,
        }

        resultado = service.criar(dados)

        repository.existe_por_nome.assert_called_once_with("Pintura")
        repository.criar.assert_called_once_with(
            {
                "nome": "Pintura",
                "status": True,
            }
        )
        assert resultado == {
            "nome": "Pintura",
            "status": True,
        }

        # Confirma que o dicionário original não foi alterado.
        assert dados["nome"] == "  Pintura  "

    def test_deve_lancar_erro_quando_nome_ja_existir(self):
        """Não deve criar serviço quando o nome estiver cadastrado."""
        repository = Mock(spec=ServicoRepository)
        repository.existe_por_nome.return_value = True

        service = ServicoService(repository)

        with pytest.raises(ServicoJaCadastradoError) as exc_info:
            service.criar(
                {
                    "nome": " Pintura ",
                    "status": True,
                }
            )

        assert (
            exc_info.value.title
            == ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO
        )
        assert exc_info.value.detail == ServicoErrorMessages.NOME_JA_CADASTRADO

        repository.existe_por_nome.assert_called_once_with("Pintura")
        repository.criar.assert_not_called()
