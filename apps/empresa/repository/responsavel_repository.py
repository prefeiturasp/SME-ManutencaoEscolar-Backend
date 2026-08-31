"""Repositório: único ponto de acesso ao ORM do domínio Responsável Técnico."""

from typing import Any

from django.forms.models import model_to_dict

from apps.empresa.models import ResponsavelTecnico
from apps.usuarios.models import Usuario


class ResponsavelTecnicoRepository:
    """Encapsula todo acesso ao ORM referente a Responsavel Técnico."""

    model = ResponsavelTecnico

    def bulk_criar(
        self, dados_lista: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Cria múltiplos responsáveis técnicos em uma única operação no banco.

        Args:
            dados_lista (list[dict[str, Any]]): Lista de dicionários com os
                dados de cada responsável técnico a ser criado.

        Returns:
            list[dict[str, Any]]: Dados serializados dos responsáveis
                técnicos criados.
        """
        responsaveis = [self.model(**dados) for dados in dados_lista]
        criados = self.model.objects.bulk_create(responsaveis)
        return [self._serializar(responsavel) for responsavel in criados]

    def bulk_atualizar(
        self, dados_lista: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Atualiza múltiplos responsáveis técnicos existentes.

        Cada dicionário deve conter a chave ``id`` identificando o registro
        a ser atualizado; os demais campos são aplicados na instância.

        Args:
            dados_lista (list[dict[str, Any]]): Lista de dicionários com o
                ``id`` e os campos de cada responsável técnico a atualizar.

        Returns:
            list[dict[str, Any]]: Dados serializados dos responsáveis
                técnicos atualizados.
        """
        atualizados = []
        for responsavel_dados in dados_lista:
            campos = {**responsavel_dados}
            responsavel_id = campos.pop("id")
            campos.pop("empresa_id", None)
            campos.pop("uuid", None)

            responsavel = self.model.objects.get(pk=responsavel_id)
            campos_alterados = [
                campo
                for campo, valor in campos.items()
                if getattr(responsavel, campo) != valor
            ]
            for campo in campos_alterados:
                setattr(responsavel, campo, campos[campo])
            if campos_alterados:
                responsavel.save(
                    update_fields=[*campos_alterados, "atualizado_em"]
                )

            atualizados.append(self._serializar(responsavel))
        return atualizados

    def listar_por_empresa(self, empresa_id: int) -> list[ResponsavelTecnico]:
        """
        Retorna os responsáveis técnicos ativos de uma empresa.

        Args:
            empresa_id (int): ID da empresa.

        Returns:
            list[ResponsavelTecnico]: Instâncias dos responsáveis técnicos.
        """
        return list(self.model.objects.filter(empresa_id=empresa_id))

    def remover(
        self,
        responsaveis: list[ResponsavelTecnico],
        usuario: Usuario | None = None,
    ) -> None:
        """
        Marca os responsáveis técnicos informados como deletados.

        Args:
            responsaveis (list[ResponsavelTecnico]): Instâncias a remover.
            usuario (Usuario | None): Usuário responsável pela remoção.
        """
        for responsavel in responsaveis:
            responsavel.soft_delete(usuario=usuario)

    def existe_por_empresa_e_tipo(self, empresa_id: int, tipo: str) -> bool:
        """
        Verifica se já existe responsável técnico do tipo na empresa.

        Args:
            empresa_id (int): ID da empresa.
            tipo (str): Tipo do responsável técnico.

        Returns:
            bool: True se existir, False caso contrário.
        """
        return self.model.objects.filter(
            empresa_id=empresa_id, tipo=tipo
        ).exists()

    def _serializar(self, responsavel: ResponsavelTecnico) -> dict[str, Any]:
        """
        Serializa uma instância de Responsavel Técnico em dicionário.

        Args:
            responsavel (ResponsavelTecnico): Instância do responsável
                técnico.

        Returns:
            dict[str, Any]: Dicionário contendo os dados do responsável
                técnico.
        """
        dados_responsavel = model_to_dict(responsavel)
        dados_responsavel["uuid"] = str(responsavel.uuid)
        dados_responsavel["empresa"] = responsavel.empresa
        dados_responsavel["criado_por"] = responsavel.criado_por
        dados_responsavel["atualizado_por"] = responsavel.atualizado_por
        dados_responsavel["criado_em"] = responsavel.criado_em
        dados_responsavel["atualizado_em"] = responsavel.atualizado_em
        return dados_responsavel
