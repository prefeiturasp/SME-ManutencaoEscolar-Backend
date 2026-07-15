"""Repositório responsável pelo acesso aos dados da aplicação EOL."""

import requests


class ApiEOLRepository:
    """Repositório responsável pela comunicação com o serviço EOL."""

    @staticmethod
    def post(
        url: str, headers: dict[str, str], data: str
    ) -> requests.Response:
        """
        Realiza uma requisição POST ao serviço EOL.

        Args:
            url (str): URL completa do endpoint.
            headers (dict[str, str]): Cabeçalhos HTTP enviados na requisição.
            data (str): Corpo da requisição serializado em JSON.

        Returns:
            requests.Response: Resposta HTTP retornada pelo serviço
                EOL.
        """
        return requests.post(
            url,
            headers=headers,
            data=data,
            timeout=10,
        )
