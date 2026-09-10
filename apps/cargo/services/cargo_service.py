"""Serviços relacionados ao cadastro de cargos."""

from typing import Any, cast

from django.core.exceptions import ValidationError

from apps.cargo.repository.cargo_repository import CargoRepository
from apps.usuarios.models.usuario import Usuario


class CargoService:
    """Orquestra as regras de negócio relacionadas aos cargos."""

    def __init__(
        self,
        repository: CargoRepository | None = None,
    ) -> None:
        """Inicializa o serviço responsável pelas regras de negócio.

        Args:
            repository: Repositório utilizado nas operações de persistência.
                Caso não seja informado, utiliza uma instância de
                CargoRepository.
        """
        self.repository = repository or CargoRepository()

    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Normaliza, valida e cria um cargo com seus documentos.

        Args:
            dados: Dados necessários para a criação do cargo.
            usuario: Usuário responsável pela criação do cargo.

        Returns:
            Dicionário contendo os dados do cargo criado e seus documentos.

        Raises:
            ValidationError: Quando existem documentos com nomes duplicados.
        """
        dados_normalizados = dados.copy()
        dados_normalizados["nome"] = dados_normalizados["nome"].strip()

        documentos = cast(
            list[dict[str, Any]],
            dados_normalizados.get("documentos", []),
        )

        documentos_normalizados = [
            {
                **documento,
                "nome": documento["nome"].strip(),
            }
            for documento in documentos
        ]

        self._validar_documentos_duplicados(documentos_normalizados)

        dados_normalizados["documentos"] = documentos_normalizados

        return self.repository.criar(
            dados_normalizados,
            usuario=usuario,
        )

    @staticmethod
    def _validar_documentos_duplicados(
        documentos: list[dict[str, Any]],
    ) -> None:
        """Valida se existem documentos com nomes duplicados.

        Args:
            documentos: Documentos informados no cadastro do cargo.

        Raises:
            ValidationError: Quando dois ou mais documentos possuem o
                mesmo nome.
        """
        nomes_normalizados = [
            documento["nome"].casefold()
            for documento in documentos
        ]

        if len(nomes_normalizados) != len(set(nomes_normalizados)):
            raise ValidationError(
                {
                    "documentos": [
                        "Não é permitido informar documentos com nomes "
                        "duplicados.",
                    ],
                }
            )
