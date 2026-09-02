"""Testes dos comandos de gerenciamento relacionados aos lotes."""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command


def test_comando_inativa_lotes_com_prazo_finalizado() -> None:
    """Deve executar o serviço e informar a quantidade inativada."""
    saida = StringIO()

    with patch(
        (
            "apps.lote.management.commands."
            "inativar_lotes_expirados.LoteService"
        ),
        autospec=True,
    ) as service_class:
        service = service_class.return_value
        service.inativar_lotes_com_prazo_finalizado.return_value = 3

        call_command(
            "inativar_lotes_expirados",
            stdout=saida,
        )

    service_class.assert_called_once_with()
    service.inativar_lotes_com_prazo_finalizado.assert_called_once_with()

    assert (
        "3 lote(s) com prazo finalizado foram inativados."
        in saida.getvalue()
    )
