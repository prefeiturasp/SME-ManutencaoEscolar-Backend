"""Exceções para a API de Empresa."""


class EmpresaNaoEncontradoError(Exception):
    """Levantada quando uma empresa não é encontrada."""


class EmpresaCnpjDuplicadoError(Exception):
    """Levantada quando já existe uma empresa com o mesmo CNPJ."""


class EmpresaPossuiLotesVinculadosError(Exception):
    """Indica que a empresa possui lotes que impedem sua exclusão."""

    def __init__(
        self,
        title: str,
        detail: dict[str, str | list[str]],
    ) -> None:
        """Armazena os dados que serão apresentados ao usuário."""
        self.title = title
        self.detail = detail
        super().__init__(title)


class EmpresaJaPossuiCNPJError(Exception):
    """Indica que o CNPJ já pertence a outra empresa cadastrada."""

    def __init__(self, *, title: str, detail: str) -> None:
        """Representa um cargo ou documento que já está vinculado a usuário."""
        self.title = title
        self.detail = detail
        super().__init__(detail)
