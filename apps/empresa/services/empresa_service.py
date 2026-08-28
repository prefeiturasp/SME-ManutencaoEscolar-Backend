"""Serviços de Empresa."""

from typing import Any

from django.db import transaction

from apps.empresa.models import Empresa
from apps.empresa.repository.empresa_repository import (
    EmpresaRepository,
)
from apps.empresa.services.responsavel_service import ResponsavelTecnicoService
from apps.usuarios.models import Usuario


class EmpresaService:
    """Orquestra as regras de negócio relacionadas a Empresa."""

    def __init__(
        self,
        empresa_repository: EmpresaRepository | None = None,
        responsavel_tecnico_service: ResponsavelTecnicoService | None = None,
    ) -> None:
        """Inicializa o serviço com os repositórios informados ou os padrões.

        Args:
            empresa_repository: Repositório de empresas a ser utilizado.
                Quando não informado, uma instância padrão de
                `EmpresaRepository` é criada.
            responsavel_tecnico_service: Serviço de responsáveis técnicos
                a ser utilizado. Quando não informado, uma instância padrão
                de `ResponsavelTecnicoService` é criada.
        """
        self.empresa_repository = empresa_repository or EmpresaRepository()
        self.responsavel_tecnico_service = (
            responsavel_tecnico_service or ResponsavelTecnicoService()
        )

    def criar(
        self, dados: dict[str, Any], usuario: Usuario | None = None
    ) -> dict[str, Any]:
        """Cria uma empresa e retorna seus dados serializados.

        Registra o usuário logado como responsável pela criação.

        Args:
            dados: Dados da empresa a ser criada.
            usuario: Usuário logado responsável pela criação.

        Returns:
            Dados serializados da empresa criada.
        """
        return self.criar_com_responsaveis({**dados, "criado_por": usuario})

    def criar_com_responsaveis(self, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria uma empresa e seus responsáveis técnicos em uma transação.

        Registra o usuário logado como responsável pela criação da empresa
        e de cada responsável técnico vinculado.

        Args:
            dados: Dados da empresa, incluindo a lista de responsáveis
                técnicos em "responsaveis_tecnicos".

        Returns:
            Dados serializados da empresa criada.
        """
        responsaveis_dados = dados.pop("responsaveis_tecnicos")

        with transaction.atomic():
            empresa = self.empresa_repository.criar({**dados})

            empresa["responsaveis_tecnicos"] = (
                self.responsavel_tecnico_service.bulk_criar(
                    [
                        {
                            **responsavel_dados,
                            "empresa_id": empresa["id"],
                            "criado_por": dados["criado_por"],
                        }
                        for responsavel_dados in responsaveis_dados
                    ]
                )
            )

        return empresa

    def atualizar(
        self,
        empresa: Empresa,
        dados: dict[str, Any],
        usuario: Usuario | None = None,
    ) -> dict[str, Any]:
        """Atualiza uma empresa existente e retorna seus dados serializados.

        Registra o usuário logado como responsável pela atualização. Quando
        ``dados`` contém a chave ``responsaveis_tecnicos``, a lista informada
        é sincronizada dentro de uma transação (upsert por ``uuid``:
        atualiza os existentes, cria os novos e remove os ausentes).

        Args:
            empresa: Instância da empresa a ser atualizada.
            dados: Dados a serem aplicados na atualização, podendo incluir
                a lista de responsáveis técnicos em ``responsaveis_tecnicos``.
            usuario: Usuário logado responsável pela atualização.

        Returns:
            Dados serializados da empresa atualizada.
        """
        dados = {**dados, "atualizado_por": usuario}
        responsaveis_dados = dados.pop("responsaveis_tecnicos", None)

        with transaction.atomic():
            empresa_atualizada = self.empresa_repository.atualizar(
                empresa, dados
            )
            empresa_atualizada["responsaveis_tecnicos"] = (
                self.responsavel_tecnico_service.sincronizar(
                    empresa_id=empresa_atualizada["id"],
                    dados_lista=responsaveis_dados,
                    usuario=usuario,
                )
            )

        return empresa_atualizada

    def deletar(
        self, empresa: Empresa, usuario: Usuario | None = None
    ) -> None:
        """Realiza a exclusão lógica de uma empresa.

        Registra o usuário logado como responsável pela exclusão.

        Args:
            empresa: Instância da empresa a ser deletada.
            usuario: Usuário logado responsável pela exclusão.
        """
        self.empresa_repository.deletar(empresa, usuario)
