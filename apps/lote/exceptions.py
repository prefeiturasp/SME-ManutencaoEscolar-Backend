"""Exceções relacionadas ao cadastro de lotes."""


class LoteJaCadastradoError(Exception):
    """Representa a tentativa de cadastrar um lote duplicado."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e detalhe."""
        self.title = title
        self.detail = detail
        super().__init__(detail)


class DREJaVinculadaError(Exception):
    """Representa uma DRE que já está vinculada a um lote."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e detalhe."""
        self.title = title
        self.detail = detail
        super().__init__(detail)




class DREJaVinculadaError(Exception):
    """Representa DREs que já estão associadas a um lote."""

    def __init__(
        self,
        title: str,
        detail: dict,
    ) -> None:
        """Inicializa o erro com os vínculos existentes."""
        self.title = title
        self.detail = detail

        super().__init__(detail)
