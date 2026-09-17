"""Repositório de documentos de função profissional."""

from typing import Any

from apps.profissional.models import DocumentoFuncaoProfissional


class DocumentoFuncaoProfissionalRepository:
    """Encapsula o acesso aos documentos das funções."""

    model = DocumentoFuncaoProfissional

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Cria um documento de função.

        Args:
            dados: Dicionário contendo os dados do documento a ser criado.

        Returns:
            Instância do documento criado.
        """
        documento = self.model(**dados)
        documento.full_clean()
        documento.save()
        return self._serializar(documento)

    @staticmethod
    def _serializar(documento: DocumentoFuncaoProfissional) -> dict[str, Any]:
        """
        Retorna um documento persistido em formato de dicionário.

        Args:
            documento: Instância do modelo `DocumentoFuncaoProfissional`
                a ser serializada.

        Returns:
            Dicionário representando o documento persistido.
        """
        return {
            "id": documento.id,
            "uuid": str(documento.uuid),
            "nome_original": documento.nome_original,
            "arquivo": documento.arquivo,
            "tipo": documento.tipo,
            "tipo_mime": documento.tipo_mime,
            "tamanho_bytes": documento.tamanho_bytes,
            "funcao_profissional": documento.funcao_profissional,
            "criado_por": documento.criado_por,
            "criado_em": documento.criado_em,
            "atualizado_por": documento.atualizado_por,
            "atualizado_em": documento.atualizado_em,
        }
