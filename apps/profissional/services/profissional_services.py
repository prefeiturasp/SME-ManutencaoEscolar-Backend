"""Serviços do domínio Profissional."""

from typing import Any

from django.db import transaction

from apps.profissional.exceptions import ProfissionalJaCadastradoError
from apps.profissional.models import Profissional
from apps.profissional.repository.profissional_repository import (
    ProfissionalRepository,
)
from apps.profissional.services.funcao_profissional_services import (
    FuncaoProfissionalService,
)
from apps.usuarios.models import Usuario


class ProfissionalService:
    """Orquestra as regras de negócio relacionadas a profissionais."""

    def __init__(
        self,
        profissional_repository: ProfissionalRepository | None = None,
        funcao_profissional_service: FuncaoProfissionalService | None = None,
    ) -> None:
        """
        Inicializa o serviço e repositório necessários.

        Args:
            profissional_repository: Repositório de profissionais
                a ser utilizado. Quando não informado, uma instância padrão
                de `ProfissionalRepository` é criada.
            funcao_profissional_service: Serviço de funções profissionais
                a ser utilizado. Quando não informado, uma instância padrão
                de `FuncaoProfissionalService` é criada.
        """
        self.profissional_repository = (
            profissional_repository or ProfissionalRepository()
        )
        self.funcao_profissional_service = (
            funcao_profissional_service or FuncaoProfissionalService()
        )

    @transaction.atomic
    def criar(
        self, profissionais: dict[str, Any], usuario: Usuario | None = None
    ) -> dict[str, Any]:
        """
        Cria um profissional com suas funções e documentos.

        Args:
            profissionais: Dados do profissional e suas funções.
            usuario (Usuario | None): Usuário que está realizando a operação.

        Returns:
            Dados do profissional criado, incluindo funções e documentos.
        """
        self._validar_duplicidade(
            profissionais.get("cpf"),
            profissionais.get("rg"),
        )
        dados = {**profissionais}
        funcoes = dados.pop("funcoes")
        profissional = self.profissional_repository.criar(
            {**dados, "criado_por": usuario}
        )
        funcoes_criadas = self.funcao_profissional_service.sincronizar(
            profissional["id"], funcoes, usuario
        )
        profissional["funcoes"] = funcoes_criadas
        return profissional

    def atualizar(
        self,
        profissional: Profissional,
        dados: dict[str, Any],
        usuario: Usuario | None = None,
    ) -> dict[str, Any]:
        """Atualiza e serializa um profissional existente.

        Registra o usuário logado como responsável pela atualização. Quando
        ``dados`` contém a chave ``funcoes``, a lista informada
        é sincronizada dentro de uma transação (upsert por ``uuid``:
        atualiza os existentes, cria os novos e remove os ausentes).

        Args:
            profissional: Instância do profissional a ser atualizado.
            dados: Dados a serem aplicados na atualização, podendo incluir
                a lista de funções em ``funcoes``.
            usuario: Usuário logado responsável pela atualização.

        Returns:
            Dados serializados do profissional atualizado.
        """
        self._validar_duplicidade(
            dados.get("cpf", profissional.cpf),
            dados.get("rg", profissional.rg),
            profissional_ignorado=profissional,
        )
        dados = {**dados, "atualizado_por": usuario}
        funcoes_dados = dados.pop("funcoes", None)

        with transaction.atomic():
            profissional_atualizado = self.profissional_repository.atualizar(
                profissional, dados
            )
            profissional_atualizado["funcoes"] = (
                self.funcao_profissional_service.sincronizar(
                    profissional_id=profissional_atualizado["id"],
                    dados_lista=funcoes_dados,
                    usuario=usuario,
                )
            )

        return profissional_atualizado

    @transaction.atomic
    def deletar(
        self,
        profissional: Profissional,
        usuario: Usuario | None = None,
    ) -> None:
        """Exclui logicamente um profissional.

        Args:
            profissional: Profissional a ser excluído.
            usuario: Usuário responsável pela exclusão.
        """
        self.funcao_profissional_service.remover_por_profissional(
            profissional.id, usuario
        )
        self.profissional_repository.deletar(profissional, usuario)

    def _validar_duplicidade(
        self,
        cpf: str | None,
        rg: str | None,
        profissional_ignorado: Profissional | None = None,
    ) -> None:
        """Valida se CPF e/ou RG já pertencem a outro profissional.

        Args:
            cpf: CPF informado.
            rg: RG informado.
            profissional_ignorado: Profissional desconsiderado na consulta
                durante a edição.

        Raises:
            ProfissionalJaCadastradoError: Se CPF e/ou RG já estiverem em uso
                por outro profissional ativo. O erro informa qual dos dois
                está duplicado.
        """
        duplicidade = self.profissional_repository.verificar_duplicidade(
            cpf, rg, profissional_ignorado
        )
        if any(duplicidade.values()):
            raise ProfissionalJaCadastradoError(duplicidade)
