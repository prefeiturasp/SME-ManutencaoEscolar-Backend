"""Serviços do domínio Equipe."""

from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.empresa.models import Empresa
from apps.equipe.constants import EquipeErrorMessages
from apps.equipe.exceptions import (
    EquipeJaCadastradaError,
    ProfissionaisVinculadosError,
    ProfissionalVinculadoError,
)
from apps.equipe.models import Equipe
from apps.equipe.repository import (
    EquipeRepository,
    ProfissionalEquipeRepository,
)
from apps.lote.models import Lote
from apps.usuarios.models import Usuario


class EquipeService:
    """Orquestra as regras de negócio relacionadas à criação de equipes."""

    def __init__(
        self,
        repository: EquipeRepository | None = None,
        profissional_repository: ProfissionalEquipeRepository | None = None,
    ) -> None:
        """Inicializa o serviço com os repositórios informados."""
        self.repository = repository or EquipeRepository()
        self.profissional_repository = (
            profissional_repository or ProfissionalEquipeRepository()
        )

    def busca_por_lote(self, lote: Lote) -> list[dict[str, Any]]:
        """Busca todas as equipes vinculadas ao lote.

        Args:
            lote: Lote usado na busca.

        Returns:
            Lista com os dados básicos das equipes encontradas.
        """
        return self.repository.buscar_por_lote(lote)

    @transaction.atomic
    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Valida e cria uma equipe com seus profissionais.

        Args:
            dados: Dados validados da equipe e seus vínculos.
            usuario: Usuário responsável pelo cadastro.

        Returns:
            Dicionário com os dados da equipe criada.

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
        self._validar_equipe(nome_equipe, empresa.uuid, empresa.nome)
        self._validar_profissionais_equipe(uuids_profissionais)

        equipe = self.repository.criar(dados, profissionais, usuario)
        return {
            **equipe,
            "profissionais": profissionais,
        }

    def atualizar(
        self,
        equipe: Equipe,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza uma equipe com seus profissionais.

        Args:
            equipe: Instância da equipe a ser atualizada.
            dados: Dados validados da equipe e seus vínculos.
            usuario: Usuário responsável pela atualização.

        Returns:
            Dicionário com os dados da equipe criada.

        Raises:
            ValidationError: Se um profissional estiver inativo ou já
                pertencer a outra equipe ativa.
        """
        profissionais = dados.pop("profissionais", None)
        nome_equipe = dados.get("nome", equipe.nome).strip()
        empresa = dados.get("empresa", equipe.empresa)
        situacao = dados.get("situacao", equipe.situacao)

        self._validar_atualizacao(
            equipe, nome_equipe, empresa, situacao, profissionais
        )

        with transaction.atomic():
            equipe_atualizada = self.repository.atualizar(
                equipe, dados, usuario
            )
            if profissionais is not None:
                self._sincronizar_profissionais(equipe, profissionais, usuario)

        vinculos = self.profissional_repository.listar_por_equipe(equipe)
        return {
            **equipe_atualizada,
            "profissionais": [
                {
                    "profissional": vinculo.profissional,
                    "funcao": vinculo.funcao,
                }
                for vinculo in vinculos
            ],
        }

    def _validar_atualizacao(
        self,
        equipe: Equipe,
        nome: str,
        empresa: Empresa,
        situacao: bool,
        profissionais: list[dict[str, Any]] | None,
    ) -> None:
        """Valida os dados alterados de uma equipe.

        Args:
            equipe: Instância da equipe a ser atualizada.
            nome: Novo nome da equipe.
            empresa: Nova empresa da equipe.
            situacao: Nova situação da equipe.
            profissionais: Lista de novos vínculos profissionais, se houver.

        Raises:
            ValidationError: Se um profissional estiver inativo ou já
                pertencer a outra equipe ativa.
            EquipeJaCadastradaError: Se o nome da equipe já existir para a
                empresa.
            ProfissionalVinculadoError: Se um profissional já estiver em uma
                equipe ativa.
            ProfissionaisVinculadosError: Se mais de um profissional já
                estiver em equipes ativas.
        """
        nome_ou_empresa_alterados = (
            nome.casefold() != equipe.nome.casefold()
            or empresa.uuid != equipe.empresa.uuid
        )
        if nome_ou_empresa_alterados:
            self._validar_equipe(nome, empresa.uuid, empresa.nome)

        if profissionais is not None:
            uuids = [item["profissional"].uuid for item in profissionais]
        elif situacao and not equipe.situacao:
            vinculos = self.profissional_repository.listar_por_equipe(equipe)
            uuids = [vinculo.profissional.uuid for vinculo in vinculos]
        else:
            return

        self._validar_profissionais_equipe(uuids, equipe)

    def _sincronizar_profissionais(
        self,
        equipe: Equipe,
        profissionais: list[dict[str, Any]],
        usuario: Usuario,
    ) -> None:
        """Sincroniza os vínculos de profissionais de uma equipe.

        Remove vínculos não informados, cria os novos e atualiza a função dos
        profissionais que permanecem na equipe.

        Args:
            equipe: Equipe cujos vínculos serão sincronizados.
            profissionais: Dados dos profissionais e de suas funções.
            usuario: Usuário responsável pela sincronização.
        """
        vinculos = self.profissional_repository.listar_por_equipe(equipe)
        profissionais_existentes = {
            vinculo.profissional.uuid: vinculo for vinculo in vinculos
        }
        uuids_informados = {
            item["profissional"].uuid for item in profissionais
        }

        for profissional_uuid, vinculo in profissionais_existentes.items():
            if profissional_uuid not in uuids_informados:
                self.profissional_repository.remover(vinculo, usuario)

        for dados_profissional in profissionais:
            vinculo_existente = profissionais_existentes.get(
                dados_profissional["profissional"].uuid
            )
            if vinculo_existente is None:
                self.profissional_repository.criar(
                    equipe, dados_profissional, usuario
                )
            elif (
                vinculo_existente.funcao.uuid
                != dados_profissional["funcao"].uuid
            ):
                self.profissional_repository.atualizar(
                    vinculo_existente, dados_profissional, usuario
                )

    def _validar_equipe(
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
        if self.repository.existe_equipe_empresa(nome, empresa_uuid):
            raise EquipeJaCadastradaError(
                title=EquipeErrorMessages.NOME_EQUIPE_DUPLICADO_TITULO,
                detail=(
                    EquipeErrorMessages.NOME_EQUIPE_DUPLICADO.format(
                        nome_equipe=nome,
                        nome_empresa=nome_empresa,
                    )
                ),
            )

    def _validar_profissionais_equipe(
        self, uuids: list[UUID], equipe: Equipe | None = None
    ) -> None:
        """Valida se os profissionais podem ser vinculados à equipe.

        Args:
            uuids: Lista de UUIDs dos profissionais a serem validados.
            equipe: Equipe atual, desconsiderada ao buscar outros vínculos.

        Raises:
            ValidationError: Se algum profissional estiver inativo.
            ProfissionalVinculadoError: Se um profissional já estiver em uma
                equipe ativa.
            ProfissionaisVinculadosError: Se mais de um profissional já
                estiver em equipes ativas.
        """
        if self.profissional_repository.existem_profissionais_inativos(uuids):
            raise ValidationError(
                {"profissionais": (EquipeErrorMessages.PROFISSIONAL_INATIVO)}
            )

        vinculos = (
            self.profissional_repository.obter_vinculos_com_equipes_ativas(
                uuids, equipe
            )
        )
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
