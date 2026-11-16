"""Repositório dos documentos exigidos das funções profissionais."""

from typing import Any

from apps.cargo.models import Cargo, DocumentoCargo
from apps.profissional.models import DocumentoExigidoFuncao
from apps.usuarios.models import Usuario


class DocumentoExigidoFuncaoRepository:
    """Encapsula o acesso ao ORM dos documentos exigidos de cada função."""

    model = DocumentoExigidoFuncao

    @staticmethod
    def nomes_documentos_cargo(cargo: Cargo) -> list[str]:
        """Lista os documentos exigidos hoje pelo cargo.

        Os documentos são devolvidos na ordem em que foram cadastrados no
        cargo.

        Args:
            cargo: Cargo consultado.

        Returns:
            Nomes dos documentos do cargo, ou lista vazia quando o cargo não
            exige documentos.
        """
        if not cargo.exige_documento:
            return []
        return list(
            DocumentoCargo.objects.filter(cargo=cargo)
            .order_by("id")
            .values_list("nome", flat=True)
        )

    def criar_documentos(
        self,
        funcao_id: int,
        nomes: list[str],
        usuario: Usuario | None = None,
    ) -> list[dict[str, Any]]:
        """Cria os documentos exigidos de uma função.

        Args:
            funcao_id: ID da função profissional.
            nomes: Nomes dos documentos, na ordem em que devem ser exibidos.
            usuario: Usuário que realiza a operação.

        Returns:
            Documentos exigidos criados.
        """
        documentos = [
            self.model(
                funcao_profissional_id=funcao_id,
                nome=nome,
                ordem=ordem,
                criado_por=usuario,
            )
            for ordem, nome in enumerate(nomes, start=1)
        ]
        self.model.objects.bulk_create(documentos)
        return self.listar_por_funcao(funcao_id)

    def remover_por_funcao(
        self, funcao_id: int, usuario: Usuario | None = None
    ) -> None:
        """Remove logicamente os documentos exigidos de uma função.

        Args:
            funcao_id: ID da função profissional.
            usuario: Usuário responsável pela remoção.
        """
        for documento in self.model.objects.filter(
            funcao_profissional_id=funcao_id
        ):
            documento.soft_delete(usuario=usuario)

    def listar_por_funcao(self, funcao_id: int) -> list[dict[str, Any]]:
        """Lista os documentos exigidos ativos de uma função.

        Args:
            funcao_id: ID da função profissional.

        Returns:
            Documentos exigidos, na ordem de exibição.
        """
        documentos = self.model.objects.filter(
            funcao_profissional_id=funcao_id
        )
        return [self._serializar(documento) for documento in documentos]

    @staticmethod
    def _serializar(documento: DocumentoExigidoFuncao) -> dict[str, Any]:
        """Retorna um documento exigido em formato de dicionário.

        Args:
            documento: Documento exigido a ser serializado.

        Returns:
            Dicionário representando o documento exigido.
        """
        return {
            "id": documento.id,
            "uuid": str(documento.uuid),
            "nome": documento.nome,
            "ordem": documento.ordem,
        }
