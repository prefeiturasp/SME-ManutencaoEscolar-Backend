"""Repositório responsável pelo acesso aos anexos da aplicação."""

from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import QuerySet

from apps.core.models import Anexo
from apps.usuarios.models.usuario import Usuario


class AnexoRepository:
    """Repositório responsável pelo acesso aos anexos da aplicação."""

    model = Anexo

    @staticmethod
    @transaction.atomic
    def criar(
        nome_original: str,
        tipo: str,
        tipo_mime: str,
        tamanho_bytes: int,
        arquivo: UploadedFile,
        usuario_id: int,
    ) -> dict[str, Any]:
        """Cria e persiste um novo anexo.

        O arquivo é armazenado no backend configurado e o anexo é
        associado ao usuário responsável pela criação.

        Args:
            nome_original: Nome original do arquivo enviado.
            tipo: Tipo do anexo conforme as opções definidas no modelo.
            tipo_mime: Tipo MIME do arquivo.
            tamanho_bytes: Tamanho do arquivo em bytes.
            usuario_id: Identificador do usuário responsável pela criação
            do anexo.

        Returns:
            Dicionário contendo os dados do anexo criado:
            - uuid: Identificador único do anexo.
            - nome: Nome original do arquivo.
            - tipo: Tipo do anexo.
            - tipo_mime: Tipo MIME do arquivo.
            - tamanho: Tamanho do arquivo em bytes.
            - url: URL para acesso ao arquivo armazenado.
        """
        usuario = Usuario.objects.get(id=usuario_id)
        anexo = Anexo.objects.create(
            nome_original=nome_original,
            tipo=tipo,
            tipo_mime=tipo_mime,
            tamanho_bytes=tamanho_bytes,
            arquivo=arquivo,
            criado_por=usuario,
        )
        return {
            "uuid": str(anexo.uuid),
            "nome": anexo.nome_original,
            "tipo": anexo.tipo,
            "tipo_mime": anexo.tipo_mime,
            "tamanho": anexo.tamanho_bytes,
            "url": anexo.url,
        }

    @staticmethod
    def buscar_por_uuid(
        identificador: str,
    ) -> Anexo | None:
        """Busca um anexo pelo seu identificador UUID.

        Args:
            identificador: UUID do anexo que será consultado.

        Returns:
            O anexo encontrado ou ``None`` caso não exista.
        """
        return Anexo.objects.filter(uuid=identificador).first()

    @staticmethod
    def listar(
        tipo: str | None = None,
    ) -> QuerySet[Anexo]:
        """Lista os anexos, opcionalmente filtrados por tipo.

        Args:
            tipo: Tipo do anexo utilizado como filtro. Quando ``None``,
                retorna anexos de todos os tipos.

        Returns:
            QuerySet contendo os anexos encontrados.
        """
        consulta = Anexo.objects.all()

        if tipo:
            consulta = consulta.filter(tipo=tipo)

        return consulta

    @staticmethod
    @transaction.atomic
    def atualizar(
        arquivo: Anexo,
        **dados: Any,
    ) -> Anexo:
        """Atualiza os campos informados de um anexo.

        A atualização é executada dentro de uma transação atômica para
        garantir que todas as alterações sejam persistidas ou nenhuma
        delas seja aplicada.

        Args:
            arquivo: Instância do anexo que será atualizada.
            **dados: Campos e respectivos valores que serão atualizados.

        Returns:
            O anexo após a atualização.
        """
        for campo, valor in dados.items():
            setattr(arquivo, campo, valor)

        arquivo.save(
            update_fields=[
                *dados.keys(),
                "atualizado_em",
            ],
        )

        return arquivo

    @staticmethod
    @transaction.atomic
    def excluir(
        arquivo: Anexo,
    ) -> None:
        """Exclui um anexo do banco de dados.

        A operação é executada dentro de uma transação atômica.

        Args:
            arquivo: Instância do anexo que será excluída.

        Returns:
            None.
        """
        arquivo.delete()
