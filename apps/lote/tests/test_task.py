"""Testes das tarefas assíncronas relacionadas aos lotes."""

from unittest.mock import Mock, patch

from apps.lote.tasks import executar_validade_lote


@patch("apps.lote.tasks.call_command", autospec=True)
def test_executar_validade_lote_chama_management_command(
    mock_call_command: Mock,
) -> None:
    """Deve executar o comando que inativa os lotes expirados."""
    resultado = executar_validade_lote.run()

    mock_call_command.assert_called_once_with(
        "inativar_lotes_expirados",
    )
    assert resultado is None
    assert (
        executar_validade_lote.name == "apps.lote.tasks.executar_validade_lote"
    )
