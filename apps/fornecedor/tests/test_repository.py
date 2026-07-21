"""Testes para o repositório de Fornecedor."""

from unittest.mock import patch

from apps.fornecedor.models import Fornecedor
from apps.fornecedor.repository.fornecedor_repository import (
    FornecedorRepository,
)


class TestFornecedorRepository:
    """Testes para o repositório de fornecedores."""

    def test_criar_chama_full_clean_e_save(self, fornecedor_payload_valido):
        repository = FornecedorRepository()

        with (
            patch.object(Fornecedor, "full_clean") as mock_full_clean,
            patch.object(Fornecedor, "save") as mock_save,
        ):
            fornecedor = repository.criar(fornecedor_payload_valido)

        assert isinstance(fornecedor, Fornecedor)
        assert fornecedor.nome == fornecedor_payload_valido["nome"]
        assert fornecedor.cnpj == fornecedor_payload_valido["cnpj"]
        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once_with()
