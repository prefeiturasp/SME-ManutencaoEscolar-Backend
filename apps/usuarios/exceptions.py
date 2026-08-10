"""Erros mapedos do usuário."""


class UsuarioNaoEncontradoError(Exception):
    """Indica que um usuário não foi encontrado."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição."""
        self.title = title
        self.detail = detail

        super().__init__(detail)


class EmailUsuarioNaoEncontradoError(Exception):
    """Indica que o e-mail de um usuário não foi encontrado."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição."""
        self.title = title
        self.detail = detail

        super().__init__(title, detail)
