"""Repositório para a logo das empresas."""

from functools import partial
from typing import Any

from django.db import transaction

from apps.empresa.models import LogoEmpresa
from apps.usuarios.models import Usuario


class LogoEmpresaRepository:
    """Centraliza a persistência da logo das empresas."""

    model = LogoEmpresa

    @transaction.atomic
    def substituir(
        self,
        empresa_id: int,
        dados_anexo: dict[str, Any],
        usuario: Usuario | None = None,
    ) -> dict[str, Any]:
        """Substitui a logo da empresa pela nova, removendo a anterior.

        Args:
            empresa_id: ID da empresa dona da logo.
            dados_anexo: Metadados do arquivo, já validados e preparados pelo
                ``AnexoService`` do core.
            usuario: Usuário responsável pela operação.

        Returns:
            Dados serializados da nova logo.
        """
        self.remover(empresa_id)
        logo = self.model(
            empresa_id=empresa_id,
            nome_original=dados_anexo["nome_original"],
            tipo=dados_anexo["tipo"],
            tipo_mime=dados_anexo["tipo_mime"],
            tamanho_bytes=dados_anexo["tamanho_bytes"],
            arquivo=dados_anexo["arquivo"],
            criado_por=usuario,
        )
        logo.save()
        return self._serializar(logo)

    @transaction.atomic
    def remover(self, empresa_id: int) -> None:
        """Exclui a logo da empresa e remove o arquivo após o commit.

        Args:
            empresa_id: ID da empresa dona da logo.
        """
        logos = self.model.objects.filter(empresa_id=empresa_id)

        for logo in logos:
            transaction.on_commit(partial(logo.arquivo.delete, save=False))

        logos.delete()

    def obter_url(self, empresa_id: int) -> str | None:
        """Obtém a URL da logo atual da empresa.

        Args:
            empresa_id: ID da empresa dona da logo.

        Returns:
            URL de acesso à logo ou ``None`` se a empresa não possuir logo.
        """
        logo = self.model.objects.filter(empresa_id=empresa_id).first()
        return logo.url if logo else None

    @staticmethod
    def _serializar(logo: LogoEmpresa) -> dict[str, Any]:
        """Serializa uma logo em formato de dicionário.

        Args:
            logo: Logo a ser serializada.

        Returns:
            Dicionário com ``uuid``, ``nome`` e ``arquivo_url``.
        """
        return {
            "uuid": str(logo.uuid),
            "nome": logo.nome_original,
            "arquivo_url": logo.url,
        }
