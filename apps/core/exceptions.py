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
