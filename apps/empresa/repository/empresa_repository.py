"""Repositório: único ponto de acesso ao ORM para o domínio Empresa."""

from typing import Any

from django.forms.models import model_to_dict

from apps.empresa.models import Empresa
from apps.usuarios.models import Usuario


class EmpresaRepository:
    """Encapsula todo acesso ao ORM referente a Empresa."""

    model = Empresa

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Cria uma empresa e retorna seus dados em formato de dicionário.

        Args:
            dados (dict[str, Any]): Dados da empresa a ser criada.

        Returns:
            dict[str, Any]: Dicionário contendo os dados da empresa.
        """
        empresa = self.model(**dados)
        empresa.full_clean()
        empresa.save()

        return self._serializar(empresa)

    def atualizar(
        self, empresa: Empresa, dados: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Atualiza os dados de uma empresa e retorna seu dicionário.

        Args:
            empresa (Empresa): Instância da empresa a ser atualizada.
            dados (dict[str, Any]): Dados da empresa a serem atualizados.

        Returns:
            dict[str, Any]: Dicionário contendo os dados atualizados
                da empresa.
        """
        for campo, valor in dados.items():
            setattr(empresa, campo, valor)
        empresa.full_clean()
        empresa.save()

        return self._serializar(empresa)

    def deletar(
        self, empresa: Empresa, usuario: Usuario | None = None
    ) -> None:
        """
        Marca uma empresa como deletada e registra o usuário.

        Args:
            empresa (Empresa): Instância da empresa a ser deletada.
            usuario (Usuario | None): Usuário que está realizando a deleção.
        """
        empresa.soft_delete(usuario=usuario)

    def _serializar(self, empresa: Empresa) -> dict[str, Any]:
        """
        Serializa uma instância de Empresa em dicionário.

        Args:
            empresa (Empresa): Instância da empresa a ser serializada.

        Returns:
            dict[str, Any]: Dicionário contendo os dados da empresa.
        """
        dados_empresa = model_to_dict(empresa)
        dados_empresa["id"] = empresa.id
        dados_empresa["uuid"] = str(empresa.uuid)
        return dados_empresa
