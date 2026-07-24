"""Serviços de Serviço."""

from typing import Any

from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.repository.servico_repository import ServicoRepository


class ServicoService:
    """Orquestra as regras de negócio relacionadas a Serviço."""

    def __init__(self, repository: ServicoRepository | None = None) -> None:
        """Inicializa o serviço com o repositório informado ou o padrão."""
        self.repository = repository or ServicoRepository()

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria um serviço e retorna seus dados serializados."""
        dados_normalizados = dados.copy()
        nome = dados_normalizados["nome"].strip()

        if self.repository.existe_por_nome(nome):
            raise ServicoJaCadastradoError(
                title=ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO,
                detail=ServicoErrorMessages.NOME_JA_CADASTRADO,
            )

        dados_normalizados["nome"] = nome

        return self.repository.criar(dados_normalizados)
