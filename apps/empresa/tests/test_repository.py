"""Testes para o repositório de Empresa."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from apps.empresa.exceptions import EmpresaCnpjDuplicadoError
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

    def test_atualizar_altera_campos_chama_full_clean_e_save(
        self, empresa_payload_valido
    ):
        """
        Retorno dos dados atualizados da empresa.

        Deve alterar os campos informados e retornar em dicionário.
        """
        repository = EmpresaRepository()
        empresa = Empresa(**empresa_payload_valido)

        with (
            patch.object(Empresa, "full_clean") as mock_full_clean,
            patch.object(Empresa, "save") as mock_save,
        ):
            resultado = repository.atualizar(empresa, {"nome": "Novo Nome"})

        assert isinstance(resultado, dict)
        assert resultado["nome"] == "Novo Nome"
        assert empresa.nome == "Novo Nome"
        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once_with()

    @pytest.mark.django_db
    def test_criar_com_cnpj_duplicado_levanta_erro_de_dominio(
        self, empresa_payload_valido
    ):
        """Deve traduzir a violação de unicidade do CNPJ em erro de domínio."""
        repository = EmpresaRepository()
        repository.criar(empresa_payload_valido)

        with pytest.raises(EmpresaCnpjDuplicadoError):
            repository.criar(empresa_payload_valido)

    def test_criar_com_erro_de_validacao_nao_relacionado_a_cnpj_propaga_erro(
        self, empresa_payload_valido
    ):
        """Deve propagar o erro original quando não for de CNPJ duplicado."""
        repository = EmpresaRepository()
        erro_validacao = ValidationError({"nome": ["campo obrigatório"]})

        with (
            patch.object(Empresa, "full_clean", side_effect=erro_validacao),
            pytest.raises(ValidationError) as exc_info,
        ):
            repository.criar(empresa_payload_valido)

        assert exc_info.value is erro_validacao

    @pytest.mark.django_db
    def test_atualizar_com_cnpj_duplicado_levanta_erro_de_dominio(
        self, empresa_payload_valido
    ):
        """Deve traduzir a violação de unicidade do CNPJ ao atualizar."""
        repository = EmpresaRepository()
        repository.criar(empresa_payload_valido)

        outra_empresa = repository.criar(
            {**empresa_payload_valido, "cnpj": "43210987654321"}
        )
        empresa = Empresa.objects.get(uuid=outra_empresa["uuid"])

        with pytest.raises(EmpresaCnpjDuplicadoError):
            repository.atualizar(
                empresa, {"cnpj": empresa_payload_valido["cnpj"]}
            )
