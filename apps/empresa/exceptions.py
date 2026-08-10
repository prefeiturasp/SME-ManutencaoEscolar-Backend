"""Exceções para a API de Empresa."""


class EmpresaNaoEncontradoError(Exception):
    """Levantada quando uma empresa não é encontrada."""


class EmpresaCnpjDuplicadoError(Exception):
    """Levantada quando já existe uma empresa com o mesmo CNPJ."""
