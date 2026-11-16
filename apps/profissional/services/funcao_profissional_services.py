"""Serviços das funções dos profissionais."""

from typing import Any

from django.core.exceptions import ValidationError

from apps.profissional.constants import ProfissionalErrorMessages
from apps.profissional.repository.documento_exigido_repository import (
    DocumentoExigidoFuncaoRepository,
)
from apps.profissional.repository.funcao_profissional_repository import (
    FuncaoProfissionalRepository,
)
from apps.profissional.services.documento_funcao_services import (
    DocumentoFuncaoProfissionalService,
)
from apps.usuarios.models import Usuario


class FuncaoProfissionalService:
    """Sincroniza as funções e seus documentos."""

    def __init__(
        self,
        repository: FuncaoProfissionalRepository | None = None,
        documento_service: DocumentoFuncaoProfissionalService | None = None,
        exigido_repository: DocumentoExigidoFuncaoRepository | None = None,
    ) -> None:
        """
        Inicializa o serviço e repositório necessários.

        Args:
            repository: Repositório de funções profissionais a ser utilizado.
                Quando não informado, uma instância padrão de
                `FuncaoProfissionalRepository` é criada.
            documento_service: Serviço de documentos das funções profissionais
                a ser utilizado. Quando não informado, uma instância padrão de
                `DocumentoFuncaoProfissionalService` é criada.
            exigido_repository: Repositório dos documentos exigidos da
                função. Quando não informado, uma instância padrão de
                `DocumentoExigidoFuncaoRepository` é criada.
        """
        self.repository = repository or FuncaoProfissionalRepository()
        self.documento_service = (
            documento_service or DocumentoFuncaoProfissionalService()
        )
        self.exigido_repository = (
            exigido_repository or DocumentoExigidoFuncaoRepository()
        )

    def sincronizar(
        self,
        profissional_id: int,
        dados_lista: list[dict[str, Any]],
        usuario: Usuario | None = None,
    ) -> list[dict[str, Any]]:
        """Sincroniza as funções de um profissional.

        Atualiza as funções identificadas por ``uuid``, cria as que não
        possuem identificador e remove as funções ausentes da lista.

        Args:
            profissional_id: ID do profissional ao qual as funções pertencem.
            dados_lista: Lista de dicionários contendo os dados das funções.
            usuario: Usuário que está realizando a operação.

        Returns:
            Funções sincronizadas, na mesma ordem da lista informada.

        Raises:
            ValidationError: Se uma função exigir documentos e eles não
                forem informados, ou se um UUID não pertencer ao profissional.
        """
        existentes = self.repository.listar_por_profissional(profissional_id)
        existentes_uuids = {
            str(funcao["uuid"]): funcao for funcao in existentes
        }
        uuids_informados = {
            str(dados["uuid"]) for dados in dados_lista if dados.get("uuid")
        }

        if uuids_informados - existentes_uuids.keys():
            raise ValidationError(
                {
                    "funcoes": (
                        ProfissionalErrorMessages.FUNCAO_PROFISSIONAL_NAO_ENCONTRADA
                    )
                }
            )

        for dados in dados_lista:
            if self._documentos_obrigatorios(
                dados, existentes_uuids
            ) and not dados.get("documentos"):
                raise ValidationError(
                    {
                        "documentos": (
                            ProfissionalErrorMessages.DOCUMENTOS_FUNCAO_PROFISSIONAL_OBRIGATORIOS
                        )
                    }
                )

        for funcao_existente in existentes:
            if str(funcao_existente["uuid"]) not in uuids_informados:
                self.repository.remover(funcao_existente, usuario)

        funcoes: list[dict[str, Any]] = []
        for funcao_dados in dados_lista:
            dados = {**funcao_dados}
            documentos = dados.pop("documentos", [])
            uuid = dados.get("uuid")
            funcao_nova = not uuid
            if uuid:
                funcao_existente = existentes_uuids[str(uuid)]
                funcao_nova = funcao_existente["cargo"].pk != dados["cargo"].pk
                funcao_serializada = self.repository.atualizar(
                    funcao_existente,
                    {**dados, "atualizado_por": usuario},
                )
            else:
                funcao_serializada = self.repository.criar(
                    {
                        **dados,
                        "profissional_id": profissional_id,
                        "criado_por": usuario,
                    }
                )
            if funcao_nova:
                self._registrar_documentos_exigidos(
                    funcao_serializada["id"], dados["cargo"], usuario
                )
            documentos_criados = self.documento_service.sincronizar(
                funcao_serializada["id"],
                documentos,
                usuario,
                funcao_nova=funcao_nova,
            )
            funcao_serializada["documentos"] = documentos_criados
            funcao_serializada["documentos_exigidos"] = (
                self.exigido_repository.listar_por_funcao(
                    funcao_serializada["id"]
                )
            )
            funcoes.append(funcao_serializada)
        return funcoes

    def _registrar_documentos_exigidos(
        self,
        funcao_id: int,
        cargo: Any,
        usuario: Usuario | None,
    ) -> None:
        """Copia os documentos do cargo para a função no momento do vínculo.

        A cópia substitui a anterior, se houver, e só é refeita quando o
        cargo é vinculado novamente. Editar o cadastro do cargo depois não
        altera os documentos exigidos desta função.

        Args:
            funcao_id: ID da função profissional.
            cargo: Cargo vinculado à função.
            usuario: Usuário que realiza a operação.
        """
        self.exigido_repository.remover_por_funcao(funcao_id, usuario)
        self.exigido_repository.criar_documentos(
            funcao_id,
            self.exigido_repository.nomes_documentos_cargo(cargo),
            usuario,
        )

    def _documentos_obrigatorios(
        self,
        dados: dict[str, Any],
        existentes_uuids: dict[str, dict[str, Any]],
    ) -> bool:
        """Indica se a função precisa receber documentos.

        Uma função já cadastrada sem documentos não é obrigada a recebê-los
        quando o cargo passa a exigi-los depois do vínculo. A atualização é
        opcional: o usuário remove e adiciona o cargo novamente para isso.

        Args:
            dados: Dados da função informada.
            existentes_uuids: Funções atuais do profissional por ``uuid``.

        Returns:
            ``True`` quando os documentos são obrigatórios para a função.
        """
        if not dados["cargo"].exige_documento:
            return False
        uuid = dados.get("uuid")
        if not uuid:
            return True
        return self.documento_service.possui_documentos(
            existentes_uuids[str(uuid)]["id"]
        )

    def remover_por_profissional(
        self,
        profissional_id: int,
        usuario: Usuario | None = None,
    ) -> None:
        """Remove as funções vinculadas a um profissional.

        Args:
            profissional_id: ID do profissional dono das funções.
            usuario: Usuário responsável pela remoção.
        """
        funcoes = self.repository.listar_por_profissional(profissional_id)
        for funcao in funcoes:
            self.documento_service.sincronizar(
                funcao_id=funcao["id"],
                documentos_lista=[],
                usuario=usuario,
            )
            self.repository.remover(funcao, usuario)
