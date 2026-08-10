"""Testes para o repositório de Empresa."""

from unittest.mock import patch

from apps.empresa.models import Empresa
from apps.empresa.repository.empresa_repository import (
    EmpresaRepository,
)


class TestEmpresaRepository:
    """Testes para o repositório de empresas."""

    def test_criar_chama_full_clean_e_save(self, empresa_payload_valido):
        """
        Retorno dos dados da empresa.

        Deve retornar os dados em formato de dicionário.
        """
        repository = EmpresaRepository()

        with (
            patch.object(Empresa, "full_clean") as mock_full_clean,
            patch.object(Empresa, "save") as mock_save,
        ):
            empresa = repository.criar(empresa_payload_valido)

        assert isinstance(empresa, dict)
        assert empresa["nome"] == empresa_payload_valido["nome"]
        assert empresa["cnpj"] == empresa_payload_valido["cnpj"]
        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once_with()
