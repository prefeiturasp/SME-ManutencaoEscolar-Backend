"""Serviços de documentos das funções profissionais."""

from typing import Any

from django.core.exceptions import ValidationError

from apps.core.services.anexo_service import AnexoService
from apps.profissional.constants import ProfissionalErrorMessages
from apps.profissional.repository.documento_exigido_repository import (
    DocumentoExigidoFuncaoRepository,
)
from apps.profissional.repository.documento_funcao_repository import (
    DocumentoFuncaoProfissionalRepository,
)
from apps.usuarios.models import Usuario


class DocumentoFuncaoProfissionalService:
    """Sincroniza documentos vinculados a uma função profissional."""

    def __init__(
        self,
        repository: DocumentoFuncaoProfissionalRepository | None = None,
        anexo_service: AnexoService | None = None,
        exigido_repository: DocumentoExigidoFuncaoRepository | None = None,
    ) -> None:
        """
        Inicializa o repositório de documentos das funções profissionais.

        Args:
            repository: Repositório de documentos das funções profissionais
                a ser utilizado. Quando não informado, uma instância padrão de
                `DocumentoFuncaoProfissionalRepository` é criada.
            anexo_service: Serviço de anexos a ser utilizado. Quando
                não informado, uma instância padrão de `AnexoService` é criada.
            exigido_repository: Repositório dos documentos exigidos da
                função. Quando não informado, uma instância padrão de
                `DocumentoExigidoFuncaoRepository` é criada.
        """
        self.repository = repository or DocumentoFuncaoProfissionalRepository()
        self.anexo_service = anexo_service or AnexoService()
        self.exigido_repository = (
            exigido_repository or DocumentoExigidoFuncaoRepository()
        )

    def possui_documentos(self, funcao_id: int) -> bool:
        """Informa se a função já possui documentos anexados.

        Args:
            funcao_id: ID da função profissional.

        Returns:
            ``True`` quando a função tem ao menos um documento ativo.
        """
        return bool(self.repository.listar_por_funcao(funcao_id))

    def sincronizar(
        self,
        funcao_id: int,
        documentos_lista: list[dict[str, Any]],
        usuario: Usuario | None = None,
        funcao_nova: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Sincroniza os documentos informados com os documentos da função.

        Cada arquivo novo é ligado ao documento exigido da função pelo
        ``nome_documento`` informado. Arquivos sem nome ocupam, na ordem, os
        documentos que ainda estão sem arquivo.

        Args:
            funcao_id: ID da função à qual os documentos pertencem.
            documentos_lista: Lista contendo os dados dos documentos.
            usuario: Usuário que está realizando a operação.
            funcao_nova: Indica que a função acabou de ser vinculada ao cargo.
                Nesse caso todos os documentos exigidos precisam de arquivo.
                Em uma função já existente só precisam continuar com arquivo
                os documentos que já tinham um.

        returns:
            Lista dos novos documentos criados.

        Raises:
            ValidationError: Se um UUID informado não pertencer à função, se
                um documento exigido ficar sem arquivo, se houver mais de um
                arquivo para o mesmo documento ou se o nome informado não for
                um documento exigido da função.
        """
        existentes = self.repository.listar_por_funcao(funcao_id)
        existentes_uuids = {str(documento["uuid"]) for documento in existentes}
        documentos_uuids_preservados = [
            str(dados["uuid"])
            for dados in documentos_lista
            if dados.get("uuid") is not None
        ]

        if set(documentos_uuids_preservados) - existentes_uuids:
            raise ValidationError(
                {
                    "documentos": (
                        ProfissionalErrorMessages.DOCUMENTO_FUNCAO_NAO_ENCONTRADO
                    )
                }
            )

        exigidos = self.exigido_repository.listar_por_funcao(funcao_id)
        novos = [d for d in documentos_lista if d.get("uuid") is None]
        preservados = set(documentos_uuids_preservados)
        cobertos = [
            documento["documento_exigido_id"]
            for documento in existentes
            if str(documento["uuid"]) in preservados
            and documento["documento_exigido_id"] is not None
        ]
        atribuicoes = self._atribuir_documentos_exigidos(
            exigidos, novos, cobertos
        )
        self._validar_cobertura(
            exigidos=exigidos,
            existentes=existentes,
            cobertos=[*cobertos, *(a for a in atribuicoes if a is not None)],
            funcao_nova=funcao_nova,
        )

        documentos_criados = []
        for documento in documentos_lista:
            if documento.get("uuid") is None:
                arquivo = documento["arquivo"]
                dados = self.anexo_service.validar_e_preparar_anexo(
                    arquivo=arquivo,
                    id_usuario=usuario.id if usuario is not None else None,
                )
                dados.pop("usuario_id", None)

                documento = self.repository.criar(
                    {
                        **dados,
                        "documento_exigido_id": atribuicoes.pop(0),
                        "funcao_profissional_id": funcao_id,
                        "criado_por": usuario,
                    }
                )
                documentos_criados.append(documento)

        documentos_uuids_preservados.extend(
            anexo["uuid"] for anexo in documentos_criados
        )

        self.repository.excluir_nao_preservados(
            funcao_id=funcao_id,
            uuids_preservados=documentos_uuids_preservados,
        )
        return documentos_criados

    @staticmethod
    def _normalizar_nome(nome: str | None) -> str:
        """Normaliza um nome de documento para comparação.

        Args:
            nome: Nome informado.

        Returns:
            Nome sem espaços extras e sem diferença de maiúsculas.
        """
        return " ".join((nome or "").split()).casefold()

    def _atribuir_documentos_exigidos(
        self,
        exigidos: list[dict[str, Any]],
        novos: list[dict[str, Any]],
        cobertos: list[int],
    ) -> list[int | None]:
        """Define a qual documento exigido cada arquivo novo corresponde.

        Args:
            exigidos: Documentos exigidos da função, em ordem de exibição.
            novos: Arquivos novos informados.
            cobertos: IDs dos documentos exigidos que já têm arquivo mantido.

        Returns:
            Para cada arquivo novo, o ID do documento exigido ou ``None``
            quando a função não possui documentos exigidos para ocupar.

        Raises:
            ValidationError: Se o nome não for de um documento exigido ou se
                dois arquivos disputarem o mesmo documento.
        """
        por_nome = {
            self._normalizar_nome(exigido["nome"]): exigido["id"]
            for exigido in exigidos
        }
        usados = set(cobertos)
        if len(usados) != len(cobertos):
            self._erro_documento(
                ProfissionalErrorMessages.DOCUMENTO_FUNCAO_DUPLICADO
            )

        atribuicoes: list[int | None] = [None] * len(novos)
        for indice, documento in enumerate(novos):
            nome = self._normalizar_nome(documento.get("nome_documento"))
            if not nome or not exigidos:
                continue
            exigido_id = por_nome.get(nome)
            if exigido_id is None:
                self._erro_documento(
                    ProfissionalErrorMessages.DOCUMENTO_NAO_PERTENCE_A_FUNCAO
                )
            if exigido_id in usados:
                self._erro_documento(
                    ProfissionalErrorMessages.DOCUMENTO_FUNCAO_DUPLICADO
                )
            usados.add(exigido_id)
            atribuicoes[indice] = exigido_id

        livres = iter(
            exigido["id"]
            for exigido in exigidos
            if exigido["id"] not in usados
        )
        for indice, documento in enumerate(novos):
            if atribuicoes[indice] is None and not self._normalizar_nome(
                documento.get("nome_documento")
            ):
                atribuicoes[indice] = next(livres, None)
        return atribuicoes

    def _validar_cobertura(
        self,
        exigidos: list[dict[str, Any]],
        existentes: list[dict[str, Any]],
        cobertos: list[int],
        funcao_nova: bool,
    ) -> None:
        """Garante que os documentos exigidos continuem com arquivo.

        Args:
            exigidos: Documentos exigidos da função.
            existentes: Arquivos que a função tinha antes da sincronização.
            cobertos: IDs dos documentos exigidos com arquivo após a
                sincronização.
            funcao_nova: Se a função acabou de ser vinculada ao cargo.

        Raises:
            ValidationError: Se um documento exigido ficar sem arquivo.
        """
        if funcao_nova:
            obrigatorios = {exigido["id"] for exigido in exigidos}
        else:
            obrigatorios = {
                documento["documento_exigido_id"]
                for documento in existentes
                if documento["documento_exigido_id"] is not None
            }
        if obrigatorios - set(cobertos):
            self._erro_documento(
                ProfissionalErrorMessages.DOCUMENTOS_FUNCAO_PROFISSIONAL_OBRIGATORIOS
            )

    @staticmethod
    def _erro_documento(mensagem: str) -> None:
        """Interrompe a sincronização com um erro no campo documentos.

        Args:
            mensagem: Mensagem do erro.

        Raises:
            ValidationError: Sempre.
        """
        raise ValidationError({"documentos": mensagem})
