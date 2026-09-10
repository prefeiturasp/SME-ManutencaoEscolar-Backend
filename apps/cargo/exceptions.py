"""Exceções relacionadas ao domínio de cargos."""

from rest_framework import status
from rest_framework.exceptions import APIException


class CargoInstabilidadeError(APIException):
    """Representa uma instabilidade durante o cadastro do cargo."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Não foi possível cadastrar o cargo."
    default_code = "cargo_instabilidade"
