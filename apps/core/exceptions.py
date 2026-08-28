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


class TelefoneInvalidoError(ValueError):
    """Levantado quando um telefone não contem o número de dígitos esperado."""

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

        super().__init__(title, detail)


class AnexoArquivoError(Exception):
    """Exceção para erros relacionados ao processamento de arquivos."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa uma exceção de arquivo."""
        self.title = title
        self.detail = detail
        super().__init__(title, detail)
