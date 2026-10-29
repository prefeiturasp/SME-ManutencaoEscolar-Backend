"""Repositórios do domínio de solicitações de manutenção."""

from typing import Any, cast

from django.db.models import QuerySet

from apps.solicitacao_manutencao.models import (
    FotoLocalReparo,
    ServicoManutencao,
    SolicitacaoManutencao,
)
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models import Usuario


class SolicitacaoManutencaoRepository:
    """Gerencia a persistência de solicitações de manutenção."""

    model = SolicitacaoManutencao
    campos_listagem = (
        "uuid",
        "codigo",
        "tipo_atendimento",
        "situacao",
        "data_envio",
        "fase",
    )

    def listar_por_usuario(
        self,
        usuario: Usuario | None,
    ) -> QuerySet[SolicitacaoManutencao, dict[str, Any]]:
        """Lista as solicitações visíveis para o usuário informado.

        Args:
            usuario: Usuário responsável pelas solicitações.

        Returns:
            Queryset de dicionários com todas as solicitações, limitado às de
            autoria do usuário quando seu perfil for UE, ou vazio quando não
            houver usuário.
        """
        queryset = self.model.objects.all()
        if usuario is None:
            queryset = queryset.none()
        elif usuario.perfil == PerfilAcesso.UE:
            queryset = queryset.filter(criado_por=usuario)
        return cast(
            QuerySet[SolicitacaoManutencao, dict[str, Any]],
            queryset.values(*self.campos_listagem),
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
        return {
            "id": solicitacao.id,
            "uuid": solicitacao.uuid,
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
        servico = self.model.objects.create(
            solicitacao_manutencao_id=solicitacao_id,
            criado_por=usuario,
            **dados,
        )
        return {
            "id": servico.id,
            "uuid": servico.uuid,
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
        return {
            "id": arquivo.id,
            "uuid": arquivo.uuid,
            "servico_manutencao": arquivo.servico_manutencao,
            "nome_original": arquivo.nome_original,
            "arquivo": arquivo.arquivo,
            "tipo": arquivo.tipo,
            "tipo_mime": arquivo.tipo_mime,
            "tamanho_bytes": arquivo.tamanho_bytes,
            "criado_por": arquivo.criado_por,
            "criado_em": arquivo.criado_em,
        }
