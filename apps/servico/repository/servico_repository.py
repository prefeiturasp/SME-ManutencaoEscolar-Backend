"""Repositório de serviços."""

from typing import Any
from uuid import UUID

from django.forms.models import model_to_dict

from apps.servico.models import Servico
from apps.usuarios.models.usuario import Usuario


class ServicoRepository:
    """Gerencia operações de persistência de serviços."""

    model: type[Servico] = Servico

    def existe_por_nome(
        self,
        nome: str,
        excluir_uuid: UUID | None = None,
    ) -> bool:
        """Verifica se existe um serviço ativo com o nome informado.

        Args:
            nome: Nome do serviço a ser consultado.
            excluir_uuid: UUID do serviço que deve ser desconsiderado
                na consulta.

        Returns:
            True se existir um serviço com o mesmo nome; caso contrário,
            False.
        """
        queryset = self.model.objects.filter(
            nome__iexact=nome,
            deletado_em__isnull=True,
        )

        if excluir_uuid is not None:
            queryset = queryset.exclude(uuid=excluir_uuid)

        return queryset.exists()

    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria e persiste um serviço.

        Args:
            dados: Dados utilizados na criação do serviço.
            usuario: Usuário responsável pela criação do serviço.

        Returns:
            Dicionário contendo os dados do serviço criado.
        """
        servico = self.model(
            **dados,
            criado_por=usuario,
            atualizado_por=usuario,
        )
        servico.full_clean()
        servico.save()

        dados_servico = model_to_dict(servico)
        dados_servico["id"] = servico.id
        dados_servico["uuid"] = str(servico.uuid)

        return dados_servico

    def atualizar(
        self,
        servico: Servico,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza e persiste um serviço existente.

        Args:
            servico: Instância do serviço a ser atualizada.
            dados: Dados que serão atualizados no serviço.
            usuario: Usuário responsável pela atualização.

        Returns:
            Dicionário contendo os dados atualizados do serviço.
        """
        if "nome" in dados:
            servico.nome = dados["nome"]

        if "status" in dados:
            servico.status = dados["status"]

        servico.atualizado_por = usuario
        servico.full_clean()
        servico.save()

        return model_to_dict(servico)

    def deletar(
        self,
        usuario: Usuario,
        model_servico: Servico,
    ) -> tuple[int, dict[str, int]]:
        """Realiza a exclusão lógica de do serviço.

        Registra o usuário responsável e marca o serviço como deletado,
        sem removê-lo fisicamente do banco de dados.

        Args:
            usuario: Usuário responsável pela exclusão lógica.
            model_servico: Instância do serviço a ser deletada.

        Returns:
            Tupla contendo a quantidade de registros deletados e um
            dicionário com a quantidade de exclusões por tipo de objeto.
        """
        model_servico.deletado_por = usuario
        model_servico.save(update_fields=["deletado_por"])

        return model_servico.soft_delete(usuario=usuario)
