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
    """Indica que o CNPJ já pertence a outra empresa cadastrada."""

    status_code = 400
    default_code = "cnpj_ja_cadastrado"

    def __init__(self, *, title: str, detail: str) -> None:
        """Inicializa o título e a mensagem retornados pela API.

        Args:
            title: Título do erro.
            detail: Mensagem que explica a duplicidade do CNPJ.
        """
        super().__init__(
            {
                "title": title,
                "message": detail,
            }
        )
