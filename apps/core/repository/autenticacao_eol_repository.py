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

    @staticmethod
    def get(url: str, headers: dict[str, str]) -> requests.Response:
        """
        Realiza uma requisição GET ao serviço EOL.

        Args:
            url (str): URL completa do endpoint.
            headers (dict[str, str]): Cabeçalhos HTTP enviados na requisição.

        Returns:
            requests.Response: Resposta HTTP retornada pelo serviço
                EOL.
        """
        return requests.get(
            url,
            headers=headers,
            timeout=10,
        )

    @classmethod
    def autentica_usuario(
        cls, url: str, headers: dict[str, str], data: str
    ) -> requests.Response:
        return cls.post(url, headers=headers, data=data)

    @staticmethod
    def usuario_existe(
        url: str, headers: dict[str, str], files: dict[str, tuple[None, str]]
    ) -> requests.Response:
        return requests.post(
            url,
            headers=headers,
            files=files,
            timeout=10,
        )
