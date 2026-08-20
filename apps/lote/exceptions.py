"""Exceções relacionadas ao cadastro de lotes."""


class DiretoriaRegionalJaVinculadaError(Exception):
    """Representa uma DRE que já está vinculada a um lote."""

    def __init__(self, title: str, detail: str | dict) -> None:
        """Inicializa a exceção com título e detalhe."""
        self.title = title
        self.detail = detail
        super().__init__(detail)
