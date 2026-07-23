"""Exceções relacionadas a validação/normalização de campos."""


class CnpjInvalidoError(ValueError):
    """Levantado quando um CNPJ não obedece ao formato esperado."""


class CepInvalidoError(ValueError):
    """Levantado quando um CEP não obedece ao formato esperado."""


class LinkRastreioInvalidoError(ValueError):
    """Levantado quando um link de rastreio não obedece ao formato esperado."""
