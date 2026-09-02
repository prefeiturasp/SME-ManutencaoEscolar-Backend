"""Testes das tarefas assíncronas relacionadas aos lotes."""

from unittest.mock import patch

from apps.lote.tasks import inativar_lotes_com_prazo_finalizado


def test_inativa_lotes_com_prazo_finalizado() -> None:
    """Deve executar o serviço e retornar a quantidade de lotes inativados."""
    with patch(
        "apps.lote.tasks.LoteService",
        autospec=True,
    ) as service_class:
        service = service_class.return_value
        service.inativar_lotes_com_prazo_finalizado.return_value = 3

        resultado = inativar_lotes_com_prazo_finalizado.run()

    service_class.assert_called_once_with()
    service.inativar_lotes_com_prazo_finalizado.assert_called_once_with()

    assert resultado == 3
    assert (
        inativar_lotes_com_prazo_finalizado.name
        == "lote.inativar_lotes_com_prazo_finalizado"
    )
