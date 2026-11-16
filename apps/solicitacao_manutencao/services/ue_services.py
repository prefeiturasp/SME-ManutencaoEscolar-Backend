"""Serviços do domínio de solicitações de manutenção."""

from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.core.services.anexo_service import AnexoService
from apps.solicitacao_manutencao.constants import PerfisSolicitacao
from apps.solicitacao_manutencao.models import (
    SituacaoSolicitacao,
)
from apps.solicitacao_manutencao.repository import (
    ArquivoServicoManutencaoRepository,
    ServicoManutencaoRepository,
    SolicitacaoManutencaoRepository,
)
from apps.solicitacao_manutencao.services.notificacao_service import (
    NotificacaoSolicitacaoService,
)
from apps.usuarios.models import Usuario


class SolicitacaoManutencaoUeService:
    """Orquestra a criação de solicitações de manutenção."""

    def __init__(
        self,
        repository: SolicitacaoManutencaoRepository | None = None,
        servico_repository: ServicoManutencaoRepository | None = None,
        arquivo_repository: ArquivoServicoManutencaoRepository | None = None,
        anexo_service: AnexoService | None = None,
        notificacao_service: NotificacaoSolicitacaoService | None = None,
    ) -> None:
        """Inicializa o serviço com suas dependências.

        Args:
            repository: Repositório de solicitações de manutenção.
            servico_repository: Repositório de serviços de manutenção.
            arquivo_repository: Repositório de arquivos de serviços
                de manutenção.
            anexo_service: Serviço de anexos para validação e preparação
                de arquivos.
            notificacao_service: Serviço de notificações por e-mail.
        """
        self.repository = repository or SolicitacaoManutencaoRepository()
        self.servico_repository = (
            servico_repository or ServicoManutencaoRepository()
        )
        self.arquivo_repository = (
            arquivo_repository or ArquivoServicoManutencaoRepository()
        )
        self.anexo_service = anexo_service or AnexoService()
        self.notificacao_service = (
            notificacao_service or NotificacaoSolicitacaoService()
        )

    def gerar_codigo(self) -> str:
        """Gera o próximo código numérico com sete dígitos.

        Returns:
            Próximo código sequencial preenchido com zeros à esquerda.
        """
        ultimo_codigo = self.repository.obter_ultimo_codigo().get("codigo")
        proximo_codigo = int(ultimo_codigo or 0) + 1
        return f"{proximo_codigo:07d}"

    @transaction.atomic
    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
        enviar: bool = False,
    ) -> dict[str, Any]:
        """Cria uma solicitação e seus serviços de forma atômica.

        Args:
            dados: Dados validados da solicitação e de seus serviços.
            usuario: Usuário responsável pelo cadastro.
            enviar: Indica se a solicitação deve ser enviada para a DRE.

        Returns:
            Dados da solicitação criada com seus serviços associados.
        """
        dados_servicos = dados.pop("servicos")
        if enviar:
            dados["situacao"] = SituacaoSolicitacao.AGUARDANDO_ANALISE_DRE
            dados["data_envio"] = timezone.now()
        else:
            dados["situacao"] = SituacaoSolicitacao.NAO_ENVIADO_DRE
        dados["codigo"] = self.gerar_codigo()
        dados["solicitante"] = PerfisSolicitacao.UE

        solicitacao = self.repository.criar(
            dados=dados,
            usuario=usuario,
        )
        solicitacao["servicos"] = self._criar_servicos(
            solicitacao, dados_servicos, usuario
        )
        if enviar:
            transaction.on_commit(
                lambda: self.notificacao_service.notificar_envio_para_dre(
                    solicitacao, usuario
                )
            )

        return solicitacao

    def atualizar(
        self,
        solicitacao: dict[str, Any],
        dados: dict[str, Any],
        usuario: Usuario,
        enviar: bool = False,
    ) -> dict[str, Any]:
        """Atualiza solicitação e sincroniza serviços e anexos por UUID.

        Args:
            solicitacao: Solicitação a ser atualizada.
            dados: Dados validados da solicitação e de seus serviços.
            usuario: Usuário responsável pela atualização.
            enviar: Indica se a solicitação deve ser enviada para a DRE.

        Returns:
            Dados atualizados da solicitação com seus serviços.
        """
        situacoes_editaveis = {
            SituacaoSolicitacao.NAO_ENVIADO_DRE,
            SituacaoSolicitacao.NECESSIDADE_REVISAO_UE,
        }
        if solicitacao["situacao"] not in situacoes_editaveis:
            raise ValidationError(
                {
                    "situacao": (
                        "A solicitação só pode ser editada nessa situação. "
                        "Precisa estar com a situação: "
                        "Não enviada para a DRE ou Necessidade de revisão."
                    )
                }
            )

        dados = {**dados, "atualizado_por": usuario}
        servicos = dados.pop("servicos", None)

        if enviar:
            dados["situacao"] = SituacaoSolicitacao.AGUARDANDO_ANALISE_DRE
            dados["data_envio"] = timezone.now()
        else:
            dados["situacao"] = SituacaoSolicitacao.NAO_ENVIADO_DRE

        with transaction.atomic():
            solicitacao_atualizada = self.repository.atualizar(
                solicitacao, dados, usuario
            )

            if servicos is not None:
                solicitacao_atualizada["servicos"] = (
                    self._sincronizar_servicos(
                        solicitacao["id"], servicos, usuario
                    )
                )

        return solicitacao_atualizada

    def _sincronizar_servicos(
        self,
        solicitacao_id: int,
        dados_servicos: list[dict[str, Any]],
        usuario: Usuario,
    ) -> list[dict[str, Any]]:
        """Atualiza serviços existentes, cria novos e remove os não informados.

        Args:
            solicitacao_id: Identificador da solicitação.
            dados_servicos: Serviços enviados na atualização.
            usuario: Usuário responsável pela atualização.

        Returns:
            Serviços sincronizados na ordem recebida.
        """
        servicos_existentes = (
            self.servico_repository.listar_servicos_por_solicitacao(
                solicitacao_id
            )
        )
        existentes_uuids = {
            str(servico["uuid"]): servico for servico in servicos_existentes
        }

        uuids_informados = {
            str(dados["uuid"]) for dados in dados_servicos if dados.get("uuid")
        }

        if uuids_informados - existentes_uuids.keys():
            raise ValidationError(
                {"servicos": "Serviço não encontrado na solicitação."}
            )

        # Remove serviços não informados
        for servico_existente in servicos_existentes:
            if str(servico_existente["uuid"]) not in uuids_informados:
                self.servico_repository.remover(
                    servico_existente["id"], usuario
                )

        servicos_sincronizados = []
        for dados_servico in dados_servicos:
            dados_arquivos = dados_servico.pop("arquivos", [])
            uuid_servico = dados_servico.pop("uuid", None)
            if uuid_servico:
                servico_atual = existentes_uuids[str(uuid_servico)]
                servico = self.servico_repository.atualizar(
                    servico_atual, dados_servico
                )
            else:
                servico = self.servico_repository.criar(
                    dados_servico, solicitacao_id, usuario
                )
            servico["arquivos"] = self._sincronizar_arquivos(
                servico["id"], dados_arquivos, usuario
            )
            servicos_sincronizados.append(servico)
        return servicos_sincronizados

    def _sincronizar_arquivos(
        self,
        servico_id: int,
        dados: list[dict[str, Any]],
        usuario: Usuario,
    ) -> list[dict[str, Any]]:
        """Mantém anexos informados e cria anexos novos.

        Args:
            servico_id: Identificador do serviço.
            dados: Anexos enviados na atualização.
            usuario: Usuário responsável.

        Returns:
            Anexos mantidos ou criados.
        """
        existentes = self.arquivo_repository.listar_anexos_por_servico(
            servico_id
        )
        uuids_existentes = {
            str(arquivo["uuid"]): arquivo for arquivo in existentes
        }
        uuids_informados = {
            str(arquivo["uuid"]) for arquivo in dados if arquivo.get("uuid")
        }
        if uuids_informados - uuids_existentes.keys():
            raise ValidationError(
                {"arquivos": "Arquivo não encontrado no serviço."}
            )

        # remove se não estiver na lista de informados
        self.arquivo_repository.excluir_nao_preservados(
            servico_id=servico_id,
            uuids_preservados=uuids_informados,
        )

        arquivos_preservados = [
            arquivo
            for arquivo in existentes
            if str(arquivo["uuid"]) in uuids_informados
        ]

        # Cria novos registros se não houver uuid
        for dados_arquivo in dados:
            uuid_arquivo = dados_arquivo.get("uuid")
            if uuid_arquivo is None:
                arquivo = dados_arquivo["arquivo"]
                dados_anexo = self.anexo_service.validar_e_preparar_anexo(
                    arquivo=arquivo,
                    id_usuario=usuario.id if usuario is not None else None,
                )
                dados_anexo.pop("usuario_id", None)

                documento = self.arquivo_repository.criar(
                    dados=dados_anexo,
                    servico_id=servico_id,
                    usuario=usuario,
                )

                arquivos_preservados.append(documento)
        return arquivos_preservados

    def _criar_servicos(
        self,
        solicitacao: dict[str, Any],
        dados: list[dict[str, Any]],
        usuario: Usuario,
    ) -> list[dict[str, Any]]:
        """Cria serviços de manutenção com seus respectivos arquivos.

        Args:
            solicitacao: Solicitação à qual os serviços pertencem.
            dados: Lista de dados validados dos serviços e de seus arquivos.
            usuario: Usuário responsável pelo cadastro.

        Returns:
            Lista de dados dos serviços criados com seus arquivos associados.
        """
        servicos = []
        for dados_servico in dados:
            dados_arquivos = dados_servico.pop("arquivos", [])
            servico = self.servico_repository.criar(
                dados=dados_servico,
                solicitacao_id=solicitacao["id"],
                usuario=usuario,
            )
            servico["arquivos"] = self._criar_arquivos(
                servico, dados_arquivos, usuario
            )
            servicos.append(servico)
        return servicos

    def _criar_arquivos(
        self,
        servico: dict[str, Any],
        dados: list[dict[str, Any]],
        usuario: Usuario,
    ) -> list[dict[str, Any]]:
        """Cria e associa arquivos a um serviço de manutenção.

        Args:
            servico: Dados do serviço ao qual os arquivos serão associados.
            dados: Dados validados dos arquivos que serão criados.
            usuario: Usuário responsável pela criação dos arquivos.

        Returns:
            Dados dos arquivos criados e associados ao serviço.
        """
        arquivos = []
        for dados_arquivo in dados:
            dados_anexo = self.anexo_service.validar_e_preparar_anexo(
                arquivo=dados_arquivo["arquivo"],
                id_usuario=usuario.id,
            )
            dados_anexo.pop("usuario_id", None)
            arquivo = self.arquivo_repository.criar(
                dados=dados_anexo,
                servico_id=servico["id"],
                usuario=usuario,
            )
            arquivos.append(arquivo)
        return arquivos
