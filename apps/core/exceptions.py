"""Erros mapedos do Sistema."""


class FalhaAutenticacaoError(Exception):
    """Erro de autenticação."""

    pass


class InternalError(Exception):
    """Erro interno do sistema."""

    pass


class SmeIntegracaoError(Exception):
    """Problema na integração com a SME."""

    pass


class CnpjInvalidoError(ValueError):
    """Levantado quando um CNPJ não obedece ao formato esperado."""

    pass


class CepInvalidoError(ValueError):
    """Levantado quando um CEP não obedece ao formato esperado."""

    pass


class LinkRastreioInvalidoError(ValueError):
    """Levantado quando um link de rastreio não obedece ao formato esperado."""

    pass
