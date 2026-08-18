"""Serviços de Serviço."""

from typing import Any

from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.models import Servico
from apps.servico.repository.servico_repository import ServicoRepository
from apps.usuarios.models.usuario import Usuario


class ServicoService:
    """Orquestra as regras de negócio relacionadas a Serviço."""

    def __init__(
        self,
        repository: ServicoRepository | None = None,
    ) -> None:
        """Inicializa o serviço com o repositório informado ou o padrão."""
        self.repository = repository or ServicoRepository()

    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria e retorna os dados de um serviço."""
        dados_normalizados = dados.copy()
        nome = dados_normalizados["nome"].strip()

        if self.repository.existe_por_nome(nome):
            self._lancar_erro_nome_duplicado()

        dados_normalizados["nome"] = nome

        return self.repository.criar(
            dados_normalizados,
            usuario=usuario,
        )

    def deletar(
        self,
        model_servico: Servico,
        usuario: Usuario,
    ) -> tuple[int, dict[str, int]]:
        """Realiza a exclusão lógica do serviço."""
        return self.repository.deletar(usuario, model_servico)

    def atualizar(
        self,
        servico: Servico,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza e retorna os dados de um serviço."""
        dados_normalizados = dados.copy()

        if "nome" in dados_normalizados:
            nome = dados_normalizados["nome"].strip()

            if self.repository.existe_por_nome(
                nome,
                excluir_uuid=servico.uuid,
            ):
                self._lancar_erro_nome_duplicado()

            dados_normalizados["nome"] = nome

        return self.repository.atualizar(
            servico,
            dados_normalizados,
            usuario=usuario,
        )

    @staticmethod
    def _lancar_erro_nome_duplicado() -> None:
        """Lança a exceção para um nome de serviço duplicado."""
        raise ServicoJaCadastradoError(
            title=ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO,
            detail=ServicoErrorMessages.NOME_JA_CADASTRADO,
        )
