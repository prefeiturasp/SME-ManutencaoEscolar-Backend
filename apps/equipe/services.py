"""Serviços do domínio Equipe."""

from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.equipe.constants import EquipeErrorMessages
from apps.equipe.exceptions import (
    EquipeJaCadastradaError,
    ProfissionaisVinculadosError,
    ProfissionalVinculadoError,
)
from apps.equipe.models import Equipe
from apps.equipe.repository import EquipeRepository
from apps.usuarios.models import Usuario


class EquipeService:
    """Orquestra as regras de negócio relacionadas à criação de equipes."""

    def __init__(self, repository: EquipeRepository | None = None) -> None:
        """Inicializa o serviço com o repositório informado ou o padrão."""
        self.repository = repository or EquipeRepository()

    @transaction.atomic
    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> Equipe:
        """Valida e cria uma equipe com seus profissionais.

        Args:
            dados: Dados validados da equipe e seus vínculos.
            usuario: Usuário responsável pelo cadastro.

        Returns:
            Equipe criada.

        Raises:
            ValidationError: Se um profissional estiver inativo ou já
                pertencer a outra equipe ativa.
        """
        profissionais = dados.pop("profissionais")
        uuids_profissionais = [
            item["profissional"].uuid for item in profissionais
        ]
        nome_equipe = dados.get("nome", "").strip()
        empresa = dados["empresa"]
        self.validar_equipe(nome_equipe, empresa.uuid, empresa.nome)
        self.validar_profissionais(uuids_profissionais)

        return self.repository.criar(dados, profissionais, usuario)

    def validar_equipe(
        self, nome: str, empresa_uuid: UUID, nome_empresa: str
    ) -> None:
        """Valida se a equipe já existe para a empresa.

        Args:
            nome: Nome da equipe.
            empresa_uuid: UUID da empresa.
            nome_empresa: Nome da empresa.

        Raises:
            EquipeJaCadastradaError: Se a equipe já existir para a empresa.
        """
        if self.repository.existe_equipe(nome, empresa_uuid):
            raise EquipeJaCadastradaError(
                title=EquipeErrorMessages.NOME_EQUIPE_DUPLICADO_TITULO,
                detail=(
                    EquipeErrorMessages.NOME_EQUIPE_DUPLICADO.format(
                        nome_equipe=nome,
                        nome_empresa=nome_empresa,
                    )
                ),
            )

    def validar_profissionais(self, uuids: list[UUID]) -> None:
        """Valida se os profissionais podem ser vinculados à equipe.

        Args:
            uuids: Lista de UUIDs dos profissionais a serem validados.
        Raises:
            ValidationError: Se algum profissional estiver inativo.
            ProfissionalVinculadoError: Se um profissional já estiver em uma
                equipe ativa.
            ProfissionaisVinculadosError: Se mais de um profissional já
                estiver em equipes ativas.
        """
        if self.repository.existem_profissionais_inativos(uuids):
            raise ValidationError(
                {"profissionais": (EquipeErrorMessages.PROFISSIONAL_INATIVO)}
            )

        vinculos = self.repository.obter_vinculos_com_equipes_ativas(uuids)
        profissionais_vinculados = [
            {"profissional": vinculo[1], "equipe": vinculo[2]}
            for vinculo in vinculos
        ]
        if len(profissionais_vinculados) > 1:
            raise ProfissionaisVinculadosError(
                title=EquipeErrorMessages.PROFISSIONAIS_OUTRA_EQUIPE_TITULO,
                detail={
                    "message": EquipeErrorMessages.PROFISSIONAIS_OUTRA_EQUIPE,
                    "vinculados": profissionais_vinculados,
                },
            )
        if vinculos:
            _, nome_profissional, nome_equipe = vinculos[0]
            raise ProfissionalVinculadoError(
                title=EquipeErrorMessages.PROFISSIONAL_OUTRA_EQUIPE_TITULO,
                detail=EquipeErrorMessages.PROFISSIONAL_OUTRA_EQUIPE.format(
                    nome_profissional=nome_profissional,
                    nome_equipe=nome_equipe,
                ),
            )
