"""Exceções da aplicação Serviço."""


class ServicoJaCadastradoError(Exception):
    """Indica que já existe um serviço com o nome informado."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição."""
        self.title = title
        self.detail = detail

        super().__init__(detail)

class ServicoExclusaoError(Exception):
    """Erro ao realizar a exclusão lógica de um serviço."""

    def __init__(self, title: str, detail: str) -> None:
        self.title = title
        self.detail = detail
        super().__init__(detail)
