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


class TokenInvalidoError(Exception):
    """Problema na geração de token JWT."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição."""
        self.title = title
        self.detail = detail

        super().__init__(detail)


class EnvioEmailError(Exception):
    """Erro ao enviar e-mail."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição."""
        self.title = title
        self.detail = detail

        super().__init__(detail)
