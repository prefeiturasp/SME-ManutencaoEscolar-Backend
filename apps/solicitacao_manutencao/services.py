"""Serviços do domínio de solicitações de manutenção."""

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.core.services.anexo_service import AnexoService
from apps.solicitacao_manutencao.models import (
    SituacaoSolicitacao,
)
from apps.solicitacao_manutencao.repository import (
    ArquivoServicoManutencaoRepository,
    ServicoManutencaoRepository,
    SolicitacaoManutencaoRepository,
)
from apps.usuarios.models import Usuario


class SolicitacaoManutencaoService:
    """Orquestra a criação de solicitações de manutenção."""

    def __init__(
        self,
        repository: SolicitacaoManutencaoRepository | None = None,
        servico_repository: ServicoManutencaoRepository | None = None,
        arquivo_repository: ArquivoServicoManutencaoRepository | None = None,
        anexo_service: AnexoService | None = None,
    ) -> None:
        """Inicializa o serviço com suas dependências.

        Args:
            repository: Repositório de solicitações de manutenção.
            servico_repository: Repositório de serviços de manutenção.
            arquivo_repository: Repositório de arquivos de serviços
                de manutenção.
            anexo_service: Serviço de anexos para validação e preparação
                de arquivos.
        """
        self.repository = repository or SolicitacaoManutencaoRepository()
        self.servico_repository = (
            servico_repository or ServicoManutencaoRepository()
        )
        self.arquivo_repository = (
            arquivo_repository or ArquivoServicoManutencaoRepository()
        )
        self.anexo_service = anexo_service or AnexoService()

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

        solicitacao = self.repository.criar(
            dados=dados,
            usuario=usuario,
        )
        solicitacao["servicos"] = self._criar_servicos(
            solicitacao, dados_servicos, usuario
        )

        return solicitacao

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
