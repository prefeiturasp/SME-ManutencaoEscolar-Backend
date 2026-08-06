from unittest.mock import patch

from apps.core.tasks import helchek


class TestHelchek:
    @patch("apps.core.tasks.sleep")
    @patch("apps.core.tasks.logger")
    def test_helchek_loga_inicio_e_fim_e_aguarda_60_segundos(
        self, mock_logger, mock_sleep
    ):
        helchek()

        mock_sleep.assert_called_once_with(60)
        mock_logger.info.assert_any_call("Executando tarefa...")
        mock_logger.info.assert_any_call("Tarefa finalizada!")
        assert mock_logger.info.call_count == 2
