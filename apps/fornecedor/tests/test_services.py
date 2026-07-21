"""Testes para os serviços de Fornecedor."""

from unittest.mock import Mock, patch

from apps.fornecedor.models import Fornecedor
from apps.fornecedor.repository.fornecedor_repository import (
    FornecedorRepository,
)
from apps.fornecedor.services.fornecedor_service import FornecedorService


class TestFornecedorService:
    """Testes para a classe FornecedorService."""

    def test_init_sem_repositorio_usa_repositorio_padrao(self):
        service = FornecedorService()

        assert isinstance(service.repository, FornecedorRepository)

    def test_criar_delega_para_repository(self, fornecedor_payload_valido):
        repository = Mock(spec=FornecedorRepository)
        fornecedor = Mock(spec=Fornecedor)
        repository.criar.return_value = fornecedor
        service = FornecedorService(repository=repository)

        resultado = service.criar(fornecedor_payload_valido)

        assert resultado == fornecedor
        repository.criar.assert_called_once_with(fornecedor_payload_valido)

    def test_criar_retorna_instancia_de_fornecedor(
        self, fornecedor_payload_valido
    ):
        service = FornecedorService()
        fornecedor = Fornecedor(**fornecedor_payload_valido)

        with patch.object(
            FornecedorRepository, "criar", return_value=fornecedor
        ) as mock_create:
            resultado = service.criar(fornecedor_payload_valido)

        assert resultado == fornecedor
        mock_create.assert_called_once_with(fornecedor_payload_valido)
