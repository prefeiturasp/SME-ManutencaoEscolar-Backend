"""Serviços relacionados ao cadastro de cargos."""

from typing import Any, cast

from apps.cargo.constants import CargoErrorMessages
from apps.cargo.exceptions import CargoOuDocumentoJaVinculadaError
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
            CargoOuDocumentoJaVinculadaError: Quando já existe um cargo com
                o nome informado ou existem documentos com nomes duplicados.
        """
        dados_normalizados = dados.copy()
        nome = dados_normalizados["nome"].strip()

        self._validar_cargo_duplicado(nome)

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

        self._validar_documentos_duplicados(
            documentos=documentos_normalizados,
            nome_cargo=nome,
        )

        dados_normalizados["nome"] = nome
        dados_normalizados["documentos"] = documentos_normalizados

        return self.repository.criar(
            dados_normalizados,
            usuario=usuario,
        )

    def _validar_cargo_duplicado(self, nome: str) -> None:
        """Valida se já existe um cargo com o nome informado.

        Args:
            nome: Nome normalizado do cargo.

        Raises:
            CargoOuDocumentoJaVinculadaError: Quando já existe um cargo
                não deletado com o mesmo nome.
        """
        if self.repository.existe_por_nome(nome):
            raise CargoOuDocumentoJaVinculadaError(
                title=CargoErrorMessages.CARGO_VINCULADO_TITULO,
                detail={
                    "message": CargoErrorMessages.CARGO_VINCULADO_CORPO.format(
                        nome=nome,
                    ),
                },
            )

    @staticmethod
    def _validar_documentos_duplicados(
        documentos: list[dict[str, Any]],
        nome_cargo: str,
    ) -> None:
        """Valida se existem documentos com nomes duplicados.

        Args:
            documentos: Documentos informados no cadastro do cargo.
            nome_cargo: Nome do cargo ao qual os documentos serão vinculados.

        Raises:
            CargoOuDocumentoJaVinculadaError: Quando dois ou mais documentos
                possuem o mesmo nome.
        """
        nomes_encontrados: set[str] = set()

        for documento in documentos:
            nome_documento = documento["nome"]
            nome_normalizado = nome_documento.casefold()

            if nome_normalizado in nomes_encontrados:
                raise CargoOuDocumentoJaVinculadaError(
                    title=(CargoErrorMessages.DOCUMENTO_VINCULADO_TITULO),
                    detail={
                        "message": (
                            CargoErrorMessages.DOCUMENTO_VINCULADO_CORPO.format(
                                nome_documento=nome_documento,
                                nome_cargo=nome_cargo,
                            )
                        ),
                    },
                )

            nomes_encontrados.add(nome_normalizado)
