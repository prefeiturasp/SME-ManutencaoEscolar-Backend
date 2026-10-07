"""Exceções do domínio Equipe."""


class EquipeJaCadastradaError(Exception):
    """Indica que já existe uma equipe com o nome informado na empresa."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição."""
        self.title = title
        self.detail = detail
        super().__init__(detail)


class ProfissionalVinculadoError(Exception):
    """Indica que o profissional já está vinculado a uma equipe."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição."""
        self.title = title
        self.detail = detail
        super().__init__(detail)


class ProfissionaisVinculadosError(Exception):
    """Indica que vários profissionais já estão vinculados a equipes."""

    def __init__(self, title: str, detail: str) -> None:
        """Inicializa a exceção com título e descrição."""
        self.title = title
        self.detail = detail
        super().__init__(detail)
