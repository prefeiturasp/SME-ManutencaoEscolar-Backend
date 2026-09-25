"""Repository de unidades educacionais."""

from typing import Any

from django.db import transaction

from apps.escola.models.responsavel_unidade import ResponsavelUnidade
from apps.escola.models.unidade_educacional import (
    DadosUnidadeEducacional,
    Unidadeeducacional,
)
from apps.escola.repository.responsavel_unidade_repository import (
    ResponsavelUnidadeRepository,
)
from apps.usuarios.models.usuario import Usuario
from apps.usuarios.repository.cargo_repository import CargoEOLRepository


class UnidadeEducacionalRepository:
    """Gerencia as operações de persistência de unidades educacionais."""

    model: type[Unidadeeducacional] = Unidadeeducacional
    responsavel_model: type[ResponsavelUnidade] = ResponsavelUnidade
    dados_model: type[DadosUnidadeEducacional] = DadosUnidadeEducacional

    def __init__(
        self,
        responsavel_repository: ResponsavelUnidadeRepository | None = None,
    ) -> None:
        """Inicializa o repository."""
        self.responsavel_repository = (
            responsavel_repository or ResponsavelUnidadeRepository()
        )

    def buscar_por_registro_funcional(
        self,
        registro_funcional: str,
    ) -> dict[str, Any] | None:
        """Busca um responsável pelo registro funcional.

        A operação é delegada ao repository de responsáveis.

        Args:
            registro_funcional: Registro funcional ou CPF do responsável.

        Returns:
            Dados do responsável e suas unidades ativas, ou None.
        """
        return self.responsavel_repository.buscar_por_registro_funcional(
            registro_funcional=registro_funcional,
        )

    def existe_vinculo_ativo(
        self,
        unidade: Unidadeeducacional,
        responsavel_uuid: str,
    ) -> bool:
        """Verifica se um responsável está vinculado à unidade.

        A operação é delegada ao repository de responsáveis.

        Args:
            unidade: Unidade educacional que será verificada.
            responsavel_uuid: UUID do responsável.

        Returns:
            True quando existir vínculo ativo; caso contrário, False.
        """
        return self.responsavel_repository.existe_vinculo_ativo(
            unidade=unidade,
            responsavel_uuid=responsavel_uuid,
        )

    @transaction.atomic
    def atualizar(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
        responsaveis: list[dict[str, Any]],
        usuario: Usuario | None,
    ) -> dict[str, Any]:
        """Atualiza a unidade e seus responsáveis.

        Args:
            unidade: Unidade educacional que será atualizada.
            dados: Dados principais da unidade.
            responsaveis: Responsáveis que serão atualizados ou criados.
            usuario: Usuário responsável pela operação.

        Returns:
            Dados da unidade educacional atualizada.
        """
        self._atualizar_dados_unidade(
            unidade=unidade,
            dados=dados,
        )

        for dados_responsavel in responsaveis:
            if dados_responsavel.get("uuid"):
                self._atualizar_responsavel(
                    unidade=unidade,
                    dados=dados_responsavel,
                    usuario=usuario,
                )
            else:
                self._criar_responsavel(
                    unidade=unidade,
                    dados=dados_responsavel,
                    usuario=usuario,
                )

        return self._serializar(unidade)

    def _atualizar_dados_unidade(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
    ) -> None:
        """Atualiza os dados principais e de contato da unidade.

        Args:
            unidade: Unidade educacional que será atualizada.
            dados: Dados de atualização.
        """
        unidade.status = dados["ativo"]
        unidade.full_clean()
        unidade.save()

        with transaction.atomic():
            self.dados_model.objects.update_or_create(
                unidade_educacional=unidade,
                defaults={
                    "email": dados["email"],
                    "telefone": dados["telefone"],
                },
            )

    def _atualizar_responsavel(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
        usuario: Usuario | None,
    ) -> None:
        """Atualiza um responsável já vinculado à unidade.

        A busca do vínculo e o acesso ao histórico são delegados ao
        ResponsavelUnidadeRepository.

        Args:
            unidade: Unidade educacional vinculada.
            dados: Dados do responsável.
            usuario: Usuário responsável pela operação.
        """
        cargo = self._obter_cargo(dados["cargo"])

        historico = self.responsavel_repository.buscar_vinculo_ativo(
            unidade=unidade,
            responsavel_uuid=dados["uuid"],
        )

        responsavel = historico.responsavel
        with transaction.atomic():
            responsavel.registro_funcional = dados["registro_funcional"]
            responsavel.nome = dados["nome"]
            responsavel.email = dados["email"]
            responsavel.telefone = dados["telefone"]
            responsavel.celular = dados["celular"]
            responsavel.atualizado_por = usuario

            responsavel.full_clean()
            responsavel.save()

            historico.cargo_id = cargo["id"]
            historico.atualizado_por = usuario
            historico.full_clean()
            historico.save()

    def _criar_responsavel(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
        usuario: Usuario | None,
    ) -> None:
        """Cria um responsável e seu vínculo com a unidade.

        Args:
            unidade: Unidade educacional à qual o responsável será vinculado.
            dados: Dados do responsável.
            usuario: Usuário responsável pela operação.
        """
        cargo = self._obter_cargo(codigo=dados["cargo"])
        responsavel = self.responsavel_model(
            registro_funcional=dados["registro_funcional"],
            nome=dados["nome"],
            email=dados["email"],
            telefone=dados["telefone"],
            celular=dados["celular"],
            criado_por=usuario,
            atualizado_por=usuario,
        )

        responsavel.full_clean()
        responsavel.save()

        self.responsavel_repository.criar_vinculo(
            responsavel=responsavel,
            unidade=unidade,
            id_cargo=cargo["id"],
            usuario=usuario,
        )

    @staticmethod
    def _obter_cargo(
        codigo: str,
    ) -> dict:
        """Obtém o cargo pelo código EOL.

        Args:
            codigo: Código EOL do cargo.

        Returns:
            Cargo EOL correspondente ao código informado.
        """
        cargo = CargoEOLRepository.buscar_por_codigo(int(codigo))

        if cargo is None:
            raise ValueError(f"Cargo EOL com código {codigo} não encontrado.")

        return cargo

    def _serializar(
        self,
        unidade: Unidadeeducacional,
    ) -> dict[str, Any]:
        """Serializa a unidade atualizada.

        A consulta dos responsáveis ativos é delegada ao
        ResponsavelUnidadeRepository.

        Args:
            unidade: Unidade educacional que será serializada.

        Returns:
            Dados da unidade no formato utilizado pela atualização.
        """
        dados_unidade = getattr(
            unidade,
            "dados",
            None,
        )

        responsaveis = self.responsavel_repository.listar_vinculos_ativos(
            unidade=unidade,
        )

        return {
            "email": dados_unidade.email if dados_unidade else "",
            "telefone": dados_unidade.telefone if dados_unidade else "",
            "ativo": unidade.status,
            "responsaveis": [
                {
                    "uuid": str(historico.responsavel.uuid),
                    "registro_funcional": (
                        historico.responsavel.registro_funcional
                    ),
                    "nome": historico.responsavel.nome,
                    "cargo": historico.cargo.codigo,
                    "email": historico.responsavel.email,
                    "telefone": historico.responsavel.telefone,
                    "celular": historico.responsavel.celular,
                }
                for historico in responsaveis
            ],
        }
