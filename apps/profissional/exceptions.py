"""Exceções do domínio Profissional."""


class ProfissionalJaCadastradoError(Exception):
    """Indica que o CPF e/ou o RG já pertencem a outro profissional."""

    def __init__(self, *, title: str, detail: str) -> None:
        """Armazena os dados que serão apresentados ao usuário.

        Args:
            title: Título exibido na mensagem de erro.
            detail: Mensagem que descreve qual documento está duplicado.
        """
        self.title = title
        self.detail = detail
        super().__init__(detail)
