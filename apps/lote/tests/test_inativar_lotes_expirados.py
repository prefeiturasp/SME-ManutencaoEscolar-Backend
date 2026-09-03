"""Testes dos comandos de gerenciamento relacionados aos lotes."""

from unittest.mock import patch

from django.core.management import call_command


def test_comando_inativa_lotes_com_prazo_finalizado() -> None:
    """Deve executar o serviço de inativação dos lotes vencidos."""
    with patch(
        (
            "apps.lote.management.commands."
            "inativar_lotes_expirados.LoteService"
        ),
        autospec=True,
    ) as service_class:
        service = service_class.return_value

        resultado = call_command("inativar_lotes_expirados")

    service_class.assert_called_once_with()

    service.inativar_lotes_com_prazo_finalizado.assert_called_once_with()

    assert resultado is None
