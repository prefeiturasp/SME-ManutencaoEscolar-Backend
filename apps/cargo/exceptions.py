"""Exceções relacionadas ao domínio de cargos."""

from rest_framework import status
from rest_framework.exceptions import APIException


class CargoInstabilidadeError(APIException):
    """Representa uma instabilidade durante o cadastro do cargo."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Não foi possível cadastrar o cargo."
    default_code = "cargo_instabilidade"


class CargoOuDDocumentoJaVinculadaError(Exception):
    """Representa um cargo ou documento que já está vinculado a um usuário."""

    def __init__(self, title: str, detail: str | dict) -> None:
        """Inicializa a exceção com título e detalhe."""
        self.title = title
        self.detail = detail
        super().__init__(detail)
