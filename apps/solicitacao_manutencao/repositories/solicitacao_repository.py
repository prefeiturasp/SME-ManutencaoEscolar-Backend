"""Repositório base do domínio de solicitações de manutenção."""

from typing import Any, cast

from django.db.models import QuerySet

from apps.solicitacao_manutencao.models import (
    FotoLocalReparo,
    ServicoManutencao,
    SolicitacaoManutencao,
)
from apps.usuarios.models import Usuario


class SolicitacaoManutencaoBaseRepository:
    """Operações de consulta comuns aos repositórios de solicitações."""

    model = SolicitacaoManutencao
    campos_listagem = (
        "uuid",
        "codigo",
        "tipo_atendimento",
        "solicitante",
        "situacao",
        "data_envio",
        "fase",
    )

    def listar_por_usuario(
        self, usuario: Usuario | None
    ) -> QuerySet[SolicitacaoManutencao, dict[str, Any]]:
        """Lista solicitações visíveis ao usuário.

        Args:
            usuario: Usuário para o qual as solicitações serão listadas.

        Returns:
            Queryset de dicionários com dados resumidos.

        Raises:
            NotImplementedError: Deve ser implementado pelas subclasses.
        """
        raise NotImplementedError

    def get_detalhes_solicitacao(
        self, usuario: Usuario | None, uuid: str
    ) -> dict[str, Any] | None:
        """Busca os detalhes de uma solicitação visível ao usuário.

        Args:
            usuario: Usuário responsável pela solicitação.
            uuid: UUID da solicitação.

        Returns:
            Dicionário com os detalhes ou ``None`` se não for encontrada.
        """
        campos = self.campos_listagem + (
            "id",
            "informacoes_adicionais",
            "unidade_educacional_id",
        )
        return cast(
            dict[str, Any] | None,
            self.listar_por_usuario(usuario)
            .filter(uuid=uuid)
            .values(*campos)
            .first(),
        )

    def _atualizar_campos(
        self,
        solicitacao: dict[str, Any],
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> None:
        """Atualiza os campos de uma solicitação registrando o responsável.

        Args:
            solicitacao: Dados da solicitação a atualizar.
            dados: Campos da solicitação já validados.
            usuario: Usuário responsável pela atualização.
        """
        self.model.objects.filter(pk=solicitacao["id"]).update(
            **{**dados, "atualizado_por": usuario}
        )


class ServicoManutencaoBaseRepository:
    """Operações comuns aos repositórios de serviços de manutenção."""

    model = ServicoManutencao

    def listar_servicos_por_solicitacao(
        self, solicitacao_id: int
    ) -> list[dict[str, Any]]:
        """Lista serviços ativos de uma solicitação.

        Args:
            solicitacao_id: Identificador da solicitação.

        Returns:
            Serviços serializados da solicitação.
        """
        return [
            self._serializar(servico)
            for servico in self.model.objects.filter(
                solicitacao_manutencao_id=solicitacao_id
            )
        ]

    def _serializar(self, servico: ServicoManutencao) -> dict[str, Any]:
        """Serializa um serviço de manutenção.

        Args:
            servico: Instância do serviço a ser serializado.

        Returns:
            Dicionário com os dados do serviço.
        """
        return {
            "id": servico.id,
            "uuid": str(servico.uuid),
            "solicitacao_manutencao": servico.solicitacao_manutencao,
            "servico": servico.servico,
            "servico_especifico": servico.servico_especifico,
            "local_reparo": servico.local_reparo,
            "descricao": servico.descricao,
            "criado_por": servico.criado_por,
            "criado_em": servico.criado_em,
        }


class ArquivoServicoManutencaoBaseRepository:
    """Operações comuns aos repositórios de arquivos de serviços."""

    model = FotoLocalReparo

    def listar_anexos_por_servico(
        self, servico_id: int
    ) -> list[dict[str, Any]]:
        """Lista anexos de um serviço de manutenção.

        Args:
            servico_id: Identificador do serviço.

        Returns:
            Anexos serializados do serviço.
        """
        return [
            self.serializar(arquivo)
            for arquivo in self.model.objects.filter(
                servico_manutencao_id=servico_id
            )
        ]

    def serializar(self, arquivo: FotoLocalReparo) -> dict[str, Any]:
        """Serializa um arquivo de serviço de manutenção.

        Args:
            arquivo: Instância do arquivo a ser serializado.

        Returns:
            Dicionário com os dados do arquivo.
        """
        return {
            "id": arquivo.id,
            "uuid": str(arquivo.uuid),
            "servico_manutencao": arquivo.servico_manutencao,
            "nome_original": arquivo.nome_original,
            "arquivo": arquivo.arquivo,
            "tipo": arquivo.tipo,
            "tipo_mime": arquivo.tipo_mime,
            "tamanho_bytes": arquivo.tamanho_bytes,
            "criado_por": arquivo.criado_por,
            "criado_em": arquivo.criado_em,
        }
