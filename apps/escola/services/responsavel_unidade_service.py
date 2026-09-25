"""Services de responsáveis de unidades educacionais."""

from typing import Any

from rest_framework.exceptions import ValidationError

from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.escola.repository.responsavel_unidade_repository import (
    ResponsavelUnidadeRepository,
)


class ResponsavelUnidadeService:
    """Contém as regras de negócio dos responsáveis de unidades."""

    def __init__(
        self,
        repository: ResponsavelUnidadeRepository | None = None,
    ) -> None:
        """Inicializa o service com o repository informado ou padrão."""
        self.repository = repository or ResponsavelUnidadeRepository()

    def validar_registros_funcionais(
        self,
        responsaveis: list[dict[str, Any]],
    ) -> None:
        """Valida a unicidade dos registros funcionais.

        Um RF pode permanecer associado ao próprio responsável durante uma
        atualização, mas não pode ser utilizado por outro responsável.

        Responsáveis criados pelo sincronizador não devem ter seu RF validado
        para alteração, pois o RF é controlado pelo sincronizador.

        Args:
            responsaveis: Responsáveis informados na atualização.

        Raises:
            ValidationError: Quando um registro funcional já estiver
                associado a outro responsável.
        """
        for responsavel in responsaveis:
            if responsavel.get("criado_pelo_sincronizador"):
                continue

            registro_funcional = responsavel["registro_funcional"]
            uuid = responsavel.get("uuid")

            existente = self.repository.buscar_por_registro_funcional(
                registro_funcional=registro_funcional,
            )

            if existente is None:
                continue

            if uuid and str(existente["uuid"]) == str(uuid):
                continue

            unidades = existente.get("unidades", [])

            unidades_formatadas = ", ".join(
                f"{unidade['codigo_eol']} - {unidade['nome']}"
                for unidade in unidades
            )

            mensagem = (
                f"Já existe um contato com o CPF/RF "
                f"{registro_funcional} para "
                f"unidade {unidades_formatadas}. "
                "Verifique as informações cadastradas e tente novamente."
            )

            raise ValidationError(
                {
                    "title": "Não é possível adicionar o contato",
                    "message": mensagem,
                }
            )

    def validar_responsaveis_da_unidade(
        self,
        unidade: Unidadeeducacional,
        responsaveis: list[dict[str, Any]],
    ) -> None:
        """Valida se os responsáveis informados pertencem à unidade.

        Responsáveis existentes precisam possuir um vínculo ativo com a
        unidade informada.

        Args:
            unidade: Unidade educacional que está sendo atualizada.
            responsaveis: Responsáveis informados na atualização.

        Raises:
            ValidationError: Quando um responsável existente não estiver
                vinculado à unidade.
        """
        for responsavel in responsaveis:
            uuid = responsavel.get("uuid")
            registro_funcional = responsavel["registro_funcional"]

            if not uuid:
                continue

            if not self.repository.existe_vinculo_ativo(
                unidade=unidade,
                responsavel_uuid=uuid,
            ):
                raise ValidationError(
                    {
                        "title": "Não é possível adicionar o contato",
                        "message": "O contato com o CPF/RF "
                        f"{registro_funcional} não está vinculado à unidade "
                        "educacional.",
                    }
                )
