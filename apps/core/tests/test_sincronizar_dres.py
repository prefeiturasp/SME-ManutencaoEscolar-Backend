"""Testes unitários para o comando de sincronização de DREs."""

from __future__ import annotations

from io import StringIO
from unittest.mock import Mock, patch

import pytest
import requests
from django.core.management.base import CommandError

from apps.core.management.commands.sincronizar_dres import Command
from apps.escola.models import DiretoriaRegional as Dre


class TestSincronizarDres:
    """Testes para o comando de sincronização de DREs."""

    @pytest.mark.django_db
    def test_handle_sincroniza_dres_criadas_e_atualizadas(self) -> None:
        """Deve criar novas DREs e atualizar as existentes."""
        Dre.objects.create(codigo="123", nome="Antiga", abreviacao="DRE-01")

        response = Mock(spec=requests.Response)
        response.raise_for_status.return_value = None
        response.json.return_value = [
            {"codigo": "123", "nome": "Nova", "abreviacao": "DRE-01"},
            {"codigo": "456", "nome": "Outra", "abreviacao": "DRE-02"},
        ]

        command = Command()
        command.stdout = StringIO()

        with (
            patch(
                "apps.core.management.commands.sincronizar_dres.requests.get",
                return_value=response,
            ) as mock_get,
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_URL",
                "https://api.exemplo/",
            ),
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_TOKEN",
                "token",
            ),
        ):
            command.handle()

        dre_atualizada = Dre.objects.get(codigo="123")
        assert dre_atualizada.nome == "Nova"
        assert dre_atualizada.abreviacao == "DRE-01"

        dre_criada = Dre.objects.get(codigo="456")
        assert dre_criada.nome == "Outra"
        assert dre_criada.abreviacao == "DRE-02"

        mock_get.assert_called_once_with(
            "https://api.exemplo/abrangencia/nome-abreviacao-dres",
            headers={"x-api-eol-key": "token", "accept": "text/plain"},
            timeout=30,
        )
        assert (
            "Sincronização concluída: 1 criada(s) e 1 atualizada(s)."
            in command.stdout.getvalue()
        )

    @pytest.mark.django_db
    def test_handle_ignora_registro_sem_codigo(self) -> None:
        """Deve ignorar registros sem código e registrar um aviso."""
        response = Mock(spec=requests.Response)
        response.raise_for_status.return_value = None
        response.json.return_value = [
            {"nome": "DRE sem código", "abreviacao": "DRE-03"}
        ]

        command = Command()
        command.stdout = StringIO()

        with (
            patch(
                "apps.core.management.commands.sincronizar_dres.requests.get",
                return_value=response,
            ),
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_URL",
                "https://api.exemplo",
            ),
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_TOKEN",
                "token",
            ),
            patch(
                "apps.core.management.commands.sincronizar_dres.logger.warning"
            ) as mock_warning,
        ):
            command.handle()

        assert Dre.objects.count() == 0
        mock_warning.assert_called_once()

    @pytest.mark.parametrize(
        ("url", "token"),
        [("", "token"), ("https://api.exemplo", "")],
    )
    def test_handle_levanta_erro_quando_configuracoes_nao_estao_definidas(
        self, url: str, token: str
    ) -> None:
        """
        Levanta CommandError.

        Lança erro quando URL ou token não estão definidos.
        """
        command = Command()

        with (
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_URL",
                url,
            ),
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_TOKEN",
                token,
            ),
            pytest.raises(
                CommandError,
                match="As variáveis SME_API_EOL_URL",
            ),
        ):
            command.handle()

    def test_handle_levanta_erro_quando_requisicao_falha(self) -> None:
        """Deve levantar CommandError quando a requisição HTTP falha."""
        command = Command()

        with (
            patch(
                "apps.core.management.commands.sincronizar_dres.requests.get",
                side_effect=requests.RequestException("falha"),
            ),
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_URL",
                "https://api.exemplo",
            ),
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_TOKEN",
                "token",
            ),
            pytest.raises(CommandError, match="Erro ao consultar a API"),
        ):
            command.handle()

    def test_handle_levanta_erro_quando_api_retorna_formato_invalido(
        self,
    ) -> None:
        """
        Levanta CommandError.

        Lança erro quando a API retorna um formato inválido.
        """
        response = Mock(spec=requests.Response)
        response.raise_for_status.return_value = None
        response.json.return_value = {"codigo": "123"}

        command = Command()

        with (
            patch(
                "apps.core.management.commands.sincronizar_dres.requests.get",
                return_value=response,
            ),
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_URL",
                "https://api.exemplo",
            ),
            patch(
                "apps.core.management.commands.sincronizar_dres.SME_API_EOL_TOKEN",
                "token",
            ),
            pytest.raises(
                CommandError,
                match="A API retornou um formato inválido",
            ),
        ):
            command.handle()
