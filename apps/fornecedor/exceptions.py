"""Exceções para a API de Fornecedor."""


class FornecedorNaoEncontradoError(Exception):
    """Levantada quando um fornecedor não é encontrado."""


class FornecedorCnpjDuplicadoError(Exception):
    """Levantada quando já existe um fornecedor com o mesmo CNPJ."""
