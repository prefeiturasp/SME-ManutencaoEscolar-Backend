"""Testes para o repositório de Serviço."""

from unittest.mock import patch

from apps.servico.models import Servico
from apps.servico.repository.servico_repository import ServicoRepository


class TestServicoRepository:
    """Testes para o repositório de serviços."""

    def test_criar_salva_e_retorna_os_dados(
        self,
        servico_payload_valido,
    ):
        """Deve criar, validar, salvar e retornar os dados do serviço."""
        repository = ServicoRepository()

        def atribuir_id(servico):
            servico.id = 1

        with (
            patch.object(Servico, "full_clean") as mock_full_clean,
            patch.object(
                Servico,
                "save",
                autospec=True,
                side_effect=atribuir_id,
            ) as mock_save,
        ):
            resultado = repository.criar(servico_payload_valido)

        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once()

        assert isinstance(resultado, dict)
        assert resultado["id"] == 1
        assert resultado["nome"] == servico_payload_valido["nome"]
        assert resultado["status"] == servico_payload_valido["status"]
        assert "uuid" in resultado
