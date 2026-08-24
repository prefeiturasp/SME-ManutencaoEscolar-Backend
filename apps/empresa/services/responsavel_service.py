"""Serviços de Responsavel Técnico."""

from typing import Any

from django.core.exceptions import ValidationError

from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.repository.responsavel_repository import (
    ResponsavelTecnicoRepository,
)


class ResponsavelTecnicoService:
    """Orquestra as regras de negócio relacionadas a Responsavel Técnico."""

    def __init__(self, repository: ResponsavelTecnicoRepository | None = None):
        """Inicializa o serviço com o repositório informado ou o padrão.

        Args:
            repository: Repositório de responsável técnico a ser
                utilizado. Quando não informado, uma instância padrão
                de `ResponsavelTecnicoRepository` é criada.
        """
        self.repository = repository or ResponsavelTecnicoRepository()

    def bulk_criar(
        self, dados_lista: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Cria múltiplos responsáveis e retorna seus dados serializados.

        Registra o usuário logado como responsável pela criação.

        Args:
            dados_lista: Lista de dicionários com os dados dos
                responsáveis técnicos a serem criados.
            usuario: Usuário logado responsável pela criação.

        Returns:
            Lista de dados serializados dos responsáveis técnicos criados.

        Raises:
            ValidationError: Se já existir um responsável técnico do mesmo
                tipo cadastrado para a mesma empresa.
        """
        for dados in dados_lista:
            self._validar_tipo_unico_na_empresa(
                dados["empresa_id"], dados["tipo"]
            )
        return self.repository.bulk_criar(dados_lista)

    def _validar_tipo_unico_na_empresa(
        self, empresa_id: int, tipo: str
    ) -> None:
        """
        Garante que não haja outro responsável do mesmo tipo na empresa.

        Args:
            empresa_id (int): ID da empresa.
            tipo (str): Tipo do responsável técnico.

        Raises:
            ValidationError: Se já existir um responsável técnico do mesmo
                tipo na empresa.
        """
        if self.repository.existe_por_empresa_e_tipo(empresa_id, tipo):
            mensagem = (
                EmpresaErrorMessages.RESPONSAVEL_TECNICO_TIPO_JA_CADASTRADO
            )
            raise ValidationError({"tipo": mensagem})
