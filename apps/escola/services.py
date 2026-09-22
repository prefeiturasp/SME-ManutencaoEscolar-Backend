"""Service do app escola."""

from typing import Any

from rest_framework.exceptions import ValidationError

from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.escola.repository import UnidadeEducacionalRepository
from apps.usuarios.models.usuario import Usuario


class UnidadeEducacionalService:
    """Contém as regras de negócio da unidade educacional."""

    def __init__(
        self,
        repository: UnidadeEducacionalRepository | None = None,
    ) -> None:
        """Inicializa o service com o repository informado ou padrão."""
        self.repository = repository or UnidadeEducacionalRepository()

    def atualizar(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza uma unidade educacional.

        Args:
            unidade: Unidade educacional que será atualizada.
            dados: Dados validados para atualização.
            usuario: Usuário responsável pela operação.

        Returns:
            Dados da unidade educacional atualizada.

        Raises:
            ValidationError: Quando um registro funcional já estiver
                associado a outro responsável.
        """
        dados_atualizacao = dados.copy()

        responsaveis = dados_atualizacao.pop(
            "responsaveis",
            [],
        )

        self._validar_registros_funcionais(
            responsaveis=responsaveis,
        )
        self.validar_responsaveis_da_unidade(
            unidade=unidade,
            responsaveis=responsaveis,
        )

        return self.repository.atualizar(
            unidade=unidade,
            dados=dados_atualizacao,
            responsaveis=responsaveis,
            usuario=usuario,
        )

    def _validar_registros_funcionais(
        self,
        responsaveis: list[dict[str, Any]],
    ) -> None:
        """Valida a unicidade dos registros funcionais.

        Um RF pode permanecer associado ao próprio responsável durante uma
        atualização, mas não pode ser utilizado por outro responsável.
        """
        registros_funcionais = [
            responsavel["registro_funcional"] for responsavel in responsaveis
        ]

        if len(registros_funcionais) != len(set(registros_funcionais)):
            raise ValidationError(
                {
                    "responsaveis": (
                        "Não é permitido informar o mesmo registro "
                        "funcional mais de uma vez."
                    )
                }
            )

        for responsavel in responsaveis:
            registro_funcional = responsavel["registro_funcional"]
            uuid = responsavel.get("uuid")

            existente = self.repository.buscar_por_registro_funcional(
                registro_funcional=registro_funcional,
            )

            if existente is None:
                continue

            if uuid and str(existente.uuid) == str(uuid):
                continue

            raise ValidationError(
                {
                    "responsaveis": (
                        f"O registro funcional "
                        f"{registro_funcional} já está associado "
                        "a outro responsável."
                    )
                }
            )

    def validar_responsaveis_da_unidade(
        self,
        unidade: Unidadeeducacional,
        responsaveis: list[dict[str, Any]],
    ) -> None:
        """Valida se os responsáveis informados pertencem à unidade."""
        for responsavel in responsaveis:
            uuid = responsavel.get("uuid")

            if not uuid:
                continue

            if not self.repository.existe_vinculo_ativo(
                unidade=unidade,
                responsavel_uuid=uuid,
            ):
                raise ValidationError(
                    {
                        "responsaveis": (
                            "O responsável informado não está "
                            "vinculado à unidade educacional."
                        )
                    }
                )
