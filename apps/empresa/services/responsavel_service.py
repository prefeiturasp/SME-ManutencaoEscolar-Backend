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

    def sincronizar(
        self,
        empresa_id: int,
        dados_lista: list[dict[str, Any]],
        usuario: Usuario | None = None,
    ) -> list[dict[str, Any]]:
        """Sincroniza os responsáveis técnicos de uma empresa.

        Faz o upsert usando o ``uuid`` como chave: os itens com ``uuid`` são
        atualizados no registro correspondente (mesmo que o ``tipo`` tenha
        mudado), os itens sem ``uuid`` são criados e os responsáveis
        existentes que não constam na lista são removidos.

        Args:
            empresa_id: ID da empresa dona dos responsáveis.
            dados_lista: Lista de dicionários com os dados de cada
                responsável técnico informado. Os itens que representam um
                responsável já existente devem conter o seu ``uuid``.
            usuario: Usuário logado responsável pela alteração.

        Returns:
            Lista de dados serializados dos responsáveis técnicos
            resultantes, na mesma ordem de ``dados_lista``.

        Raises:
            ValidationError: Se um ``uuid`` informado não pertencer a um
                responsável técnico da empresa.
        """
        existentes = self.repository.listar_por_empresa(empresa_id)
        existentes_uuid = {str(item.uuid): item for item in existentes}
        uuids_informados = {
            str(dados["uuid"]) for dados in dados_lista if dados.get("uuid")
        }

        if uuids_informados - existentes_uuid.keys():
            raise ValidationError(
                {
                    "responsaveis_tecnicos": (
                        EmpresaErrorMessages.RESPONSAVEL_TECNICO_NAO_ENCONTRADO
                    )
                }
            )

        para_remover = [
            item
            for item in existentes
            if str(item.uuid) not in uuids_informados
        ]
        dados_para_atualizar = [
            {
                **dados,
                "id": existentes_uuid[str(dados["uuid"])].id,
                "atualizado_por": usuario,
            }
            for dados in dados_lista
            if dados.get("uuid")
        ]
        dados_para_criar = [
            {**dados, "empresa_id": empresa_id, "criado_por": usuario}
            for dados in dados_lista
            if not dados.get("uuid")
        ]

        if para_remover:
            self.repository.remover(para_remover, usuario)

        sincronizados: dict[str, dict[str, Any]] = {}
        if dados_para_atualizar:
            for responsavel in self.repository.bulk_atualizar(
                dados_para_atualizar
            ):
                sincronizados[responsavel["tipo"]] = responsavel
        if dados_para_criar:
            for responsavel in self.repository.bulk_criar(dados_para_criar):
                sincronizados[responsavel["tipo"]] = responsavel

        return [sincronizados[dados["tipo"]] for dados in dados_lista]

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
