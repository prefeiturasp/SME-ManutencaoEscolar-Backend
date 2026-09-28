"""Exceções para a API de Empresa."""
from rest_framework.exceptions import APIException


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

class EmpresaJaPossuiCNPJ(APIException):
    status_code = 400
    default_code = "cnpj_ja_cadastrado"

    def __init__(self, *, title: str, detail: str) -> None:
        super().__init__({
            "title": title,
            "message": detail,
        })
