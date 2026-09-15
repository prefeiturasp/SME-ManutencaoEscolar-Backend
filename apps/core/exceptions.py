"""Exceções customizadas utilizadas pela aplicação Core.

Define exceções específicas para representar falhas de autenticação,
integração, validação de dados, tokens, envio de e-mails e processamento
de arquivos.
"""


class FalhaAutenticacaoError(Exception):
    """Indica uma falha durante o processo de autenticação."""

    pass


class InternalError(Exception):
    """Indica uma falha interna não tratada pela aplicação."""

    pass


class SmeIntegracaoError(Exception):
    """Indica uma falha na integração com serviços da SME."""

    pass


class CnpjInvalidoError(ValueError):
    """Indica que um CNPJ não atende ao formato esperado."""

    pass


class CepInvalidoError(ValueError):
    """Indica que um CEP não atende ao formato esperado."""

    pass


class LinkRastreioInvalidoError(ValueError):
    """Indica que um link de rastreamento não atende ao formato esperado."""

    pass


class TelefoneInvalidoError(ValueError):
    """Indica que um telefone não possui a quantidade esperada de dígitos."""

    pass


class TokenInvalidoError(Exception):
    """
    Indica um problema relacionado à validação ou processamento de token.

    Armazena um título e uma descrição destinados a serem utilizados
    pelas camadas responsáveis pelo tratamento e apresentação do erro.
    """

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição.

        Args:
            title (str): Título resumido do erro.
            detail (str): Descrição detalhada do erro.
        """
        self.title = title
        self.detail = detail

        super().__init__(detail)


class EnvioEmailError(Exception):
    """Indica uma falha durante o envio de e-mail.

    Armazena informações estruturadas para apresentação do erro pela
    camada responsável pelo tratamento da exceção.
    """

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição.

        Args:
            title (str): Título resumido do erro.
            detail (str): Descrição detalhada do erro.
        """
        self.title = title
        self.detail = detail

        super().__init__(title, detail)


class AnexoArquivoError(Exception):
    """
    Indica uma falha relacionada ao processamento de arquivos.

    Armazena informações estruturadas para permitir que as camadas
    superiores retornem uma mensagem apropriada ao cliente.
    """

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição.

        Args:
            title (str): Título resumido do erro.
            detail (str): Descrição detalhada do erro.
        """
        self.title = title
        self.detail = detail
        super().__init__(title, detail)


class EmailInvalidoError(Exception):
    """Indica que um endereço de e-mail possui formato inválido."""
