"""Repositórios do domínio de solicitações de manutenção."""

from collections.abc import Iterable
from functools import partial
from typing import Any, cast
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet

from apps.solicitacao_manutencao.models import (
    FotoLocalReparo,
    ServicoManutencao,
    SolicitacaoManutencao,
)
from apps.usuarios.models import Usuario


class SolicitacaoManutencaoRepository:
    """Gerencia a persistência de solicitações de manutenção."""

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
            usuario: Usuário responsável pelas solicitações.
        Returns:
            Queryset de dicionários com dados resumidos.
        """
        filtros: dict[str, Any] = {}
        if usuario is None:
            queryset = self.model.objects.none()
        elif usuario.perfil == "DRE":
            if usuario.diretoria_regional_id is None:
                queryset = self.model.objects.none()
            else:
                filtros["unidade_educacional__diretoria_regional_id"] = (
                    usuario.diretoria_regional_id
                )
                queryset = self.model.objects.filter(**filtros)
        elif usuario.username:
            filtros.update(
                {
                    "unidade_educacional__historico_responsaveis__ativo": True,
                    "unidade_educacional__historico_responsaveis__responsavel__"
                    "registro_funcional": usuario.username,
                }
            )
            queryset = self.model.objects.filter(**filtros)
        else:
            queryset = self.model.objects.none()

        return cast(
            QuerySet[SolicitacaoManutencao, dict[str, Any]],
            queryset.values(*self.campos_listagem),
        )

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
            "solicitante",
        )
        return cast(
            dict[str, Any] | None,
            self.listar_por_usuario(usuario)
            .filter(uuid=uuid)
            .values(*campos)
            .first(),
        )

    def criar(self, dados: dict[str, Any], usuario: Usuario) -> dict[str, Any]:
        """Cria uma solicitação de manutenção.

        Args:
            dados: Dados da solicitação.
            usuario: Usuário responsável pelo cadastro.

        Returns:
            Dicionário com os dados da solicitação criada.
        """
        solicitacao = self.model.objects.create(**dados, criado_por=usuario)
        return self._serializar(solicitacao)

    def atualizar(
        self,
        solicitacao: dict[str, Any],
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza uma solicitação acessível pela UE.

        Args:
            solicitacao: Instância da solicitação a atualizar.
            dados: Campos da solicitação já validados.
            usuario: Usuário responsável pela atualização.

        Returns:
            Dados atualizados da solicitação.
        """
        dados_atualizacao = {**dados, "atualizado_por": usuario}
        self.model.objects.filter(pk=solicitacao["id"]).update(
            **dados_atualizacao
        )
        dados_atualizados = self.model.objects.get(pk=solicitacao["id"])
        return self._serializar(dados_atualizados)

    def obter_ultimo_codigo(self) -> dict[str, str]:
        """Consulta o maior código de solicitação persistido.

        Returns:
            Dicionário com o maior código encontrado ou vazio quando não houver
            registros.
        """
        resultado = (
            self.model.dm_objects.order_by("-codigo").values("codigo").first()
        )
        return {"codigo": resultado["codigo"]} if resultado else {}

    def _serializar(
        self, solicitacao: SolicitacaoManutencao | dict[str, Any]
    ) -> dict[str, Any]:
        """Serializa uma solicitação de manutenção.

        Args:
            solicitacao: Instância ou dados da solicitação.

        Returns:
            Dicionário com os dados da solicitação.
        """
        if isinstance(solicitacao, dict):
            return {
                "id": solicitacao["id"],
                "uuid": str(solicitacao["uuid"]),
                "codigo": solicitacao["codigo"],
                "tipo_atendimento": solicitacao["tipo_atendimento"],
                "informacoes_adicionais": solicitacao[
                    "informacoes_adicionais"
                ],
                "unidade_educacional": solicitacao["unidade_educacional_id"],
                "situacao": solicitacao["situacao"],
                "data_envio": solicitacao["data_envio"],
                "fase": solicitacao["fase"],
                "criado_por": solicitacao["criado_por_id"],
                "criado_em": solicitacao["criado_em"],
            }
        return {
            "id": solicitacao.id,
            "uuid": str(solicitacao.uuid),
            "codigo": solicitacao.codigo,
            "tipo_atendimento": solicitacao.tipo_atendimento,
            "informacoes_adicionais": solicitacao.informacoes_adicionais,
            "unidade_educacional": solicitacao.unidade_educacional,
            "situacao": solicitacao.situacao,
            "data_envio": solicitacao.data_envio,
            "fase": solicitacao.fase,
            "criado_por": solicitacao.criado_por,
            "criado_em": solicitacao.criado_em,
        }


class ServicoManutencaoRepository:
    """Gerencia a persistência de serviços de manutenção."""

    model = ServicoManutencao

    def criar(
        self,
        dados: dict[str, Any],
        solicitacao_id: int,
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria um serviço associado a uma solicitação.

        Args:
            dados: Dados do serviço de manutenção.
            solicitacao_id: ID da solicitação à qual o serviço
                pertence.
            usuario: Usuário responsável pelo cadastro.

        Returns:
            Dicionário com os dados do serviço de manutenção criado.
        """
        servico = self.model(
            **dados,
            solicitacao_manutencao_id=solicitacao_id,
            criado_por=usuario,
        )
        servico.full_clean()
        servico.save()
        return self._serializar(servico)

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

    def atualizar(
        self,
        servico: dict[str, Any],
        dados: dict[str, Any],
    ) -> dict[str, Any]:
        """Atualiza um serviço e retorna seus dados serializados.

        Args:
            servico: Serviço serializado a atualizar.
            dados: Campos atualizados.

        Returns:
            Serviço atualizado em formato de dicionário.
        """
        instancia = self.model.objects.get(pk=servico["id"])
        for campo, valor in dados.items():
            setattr(instancia, campo, valor)
        instancia.full_clean()
        instancia.save()
        return self._serializar(instancia)

    def remover(self, servico_id: int, usuario: Usuario) -> None:
        """Remove logicamente um serviço de manutenção.

        Args:
            servico_id: ID do serviço a ser removido.
            usuario: Usuário responsável pela remoção.
        """
        instancia = self.model.objects.get(pk=servico_id)
        instancia.soft_delete(usuario=usuario)

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


class ArquivoServicoManutencaoRepository:
    """Gerencia a persistência de arquivos de serviços de manutenção."""

    model = FotoLocalReparo

    def criar(
        self,
        dados: dict[str, Any],
        servico_id: int,
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria um arquivo associado a um serviço de manutenção.

        Args:
            dados: Dados do arquivo.
            servico_id: Identificador do serviço ao qual o arquivo pertence.
            usuario: Usuário responsável pelo cadastro.

        Returns:
            Dicionário com os dados do arquivo do serviço criado.
        """
        arquivo = self.model.objects.create(
            servico_manutencao_id=servico_id,
            criado_por=usuario,
            **dados,
        )
        return self.serializar(arquivo)

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
            for arquivo in FotoLocalReparo.objects.filter(
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

    @transaction.atomic
    def excluir_nao_preservados(
        self,
        servico_id: int,
        uuids_preservados: Iterable[str | UUID],
    ) -> None:
        """Exclui os registros e remove os arquivos após o commit.

        Args:
            servico_id: ID do serviço dono dos arquivos.
            uuids_preservados: UUIDs dos arquivos que devem permanecer
                ativos.

        """
        arquivos_nao_preservados = self.model.objects.filter(
            servico_manutencao_id=servico_id
        ).exclude(uuid__in=uuids_preservados)

        for arquivo in arquivos_nao_preservados:
            transaction.on_commit(partial(arquivo.arquivo.delete, save=False))

        arquivos_nao_preservados.delete()
