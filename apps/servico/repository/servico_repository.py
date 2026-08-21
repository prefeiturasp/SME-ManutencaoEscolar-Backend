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
        """Verifica se existe serviço cadastrado com o mesmo nome."""
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
        """Cria e persiste um serviço."""
        servico = self.model(
            **dados, criado_por=usuario, atualizado_por=usuario
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
        """Atualiza e persiste um serviço existente."""
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
        """Marca o registro como deletado sem removê-lo fisicamente."""
        model_servico.deletado_por = usuario

        model_servico.save(
            update_fields=["deletado_por"],
        )

        return model_servico.soft_delete(usuario=usuario)
