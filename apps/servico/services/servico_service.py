"""Serviços relacionados ao gerenciamento de serviços."""

from typing import Any

from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.models import Servico
from apps.servico.repository.servico_repository import ServicoRepository
from apps.usuarios.models.usuario import Usuario


class ServicoService:
    """Orquestra as regras de negócio relacionadas aos serviços."""

    def __init__(
        self,
        repository: ServicoRepository | None = None,
    ) -> None:
        """Inicializa o serviço responsável pelas regras de negócio.

        Args:
            repository: Repositório utilizado nas operações de persistência.
                Caso não seja informado, utiliza uma instância de
                ServicoRepository.
        """
        self.repository = repository or ServicoRepository()

    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria um serviço após validar e normalizar seus dados.

        Args:
            dados: Dados utilizados na criação do serviço.
            usuario: Usuário responsável pela criação do serviço.

        Returns:
            Dicionário contendo os dados do serviço criado.

        Raises:
            ServicoJaCadastradoError: Se já existir um serviço ativo com
                o nome informado.
        """
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
        """Realiza a exclusão lógica de um serviço.

        Registra o usuário responsável e delega a exclusão lógica ao
        repositório.

        Args:
            model_servico: Instância do serviço a ser deletada.
            usuario: Usuário responsável pela exclusão lógica.

        Returns:
            Tupla contendo a quantidade de registros deletados e um
            dicionário com a quantidade de exclusões por tipo de objeto.
        """
        return self.repository.deletar(usuario, model_servico)

    def atualizar(
        self,
        servico: Servico,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza um serviço após validar e normalizar seus dados.

        Args:
            servico: Instância do serviço a ser atualizada.
            dados: Dados que serão atualizados no serviço.
            usuario: Usuário responsável pela atualização.

        Returns:
            Dicionário contendo os dados atualizados do serviço.

        Raises:
            ServicoJaCadastradoError: Se já existir outro serviço ativo
                com o nome informado.
        """
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
        """Lança uma exceção para um nome de serviço duplicado.

        Raises:
            ServicoJaCadastradoError: Sempre que o método for chamado.
        """
        raise ServicoJaCadastradoError(
            title=ServicoErrorMessages.NOME_JA_CADASTRADO_TITULO,
            detail=ServicoErrorMessages.NOME_JA_CADASTRADO,
        )
