"""Serviços de Responsavel Técnico."""

from typing import Any

from django.core.exceptions import ValidationError

from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.repository.responsavel_repository import (
    ResponsavelTecnicoRepository,
)
from apps.usuarios.models import Usuario


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

    def criar(
        self, dados: dict[str, Any], usuario: Usuario | None = None
    ) -> dict[str, Any]:
        """Cria um responsável técnico e retorna seus dados serializados.

        Registra o usuário logado como responsável pela criação.

        Args:
            dados: Dados do responsável técnico a ser criado.
            usuario: Usuário logado responsável pela criação.

        Returns:
            Dados serializados do responsável técnico criado.

        Raises:
            ValidationError: Se já existir um responsável técnico do mesmo
                tipo cadastrado para a mesma empresa.
        """
        self._validar_tipo_unico_na_empresa(dados["empresa"].id, dados["tipo"])
        return self.repository.criar({**dados, "criado_por": usuario})

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
