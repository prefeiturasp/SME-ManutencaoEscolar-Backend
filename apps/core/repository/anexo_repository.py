"""Repositório responsável pelo acesso aos anexos da aplicação."""

from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import ObjectDoesNotExist

from apps.core.exceptions import AnexoArquivoError
from apps.core.models import Anexo
from apps.usuarios.exceptions import UsuarioNaoEncontradoError
from apps.usuarios.models.usuario import Usuario


class AnexoRepository:
    """Repositório responsável pelo acesso aos anexos da aplicação."""

    model = Anexo

    def _retorna_anexo_em_dicionario(self, anexo: Anexo) -> dict[str, Any]:
        """Transforma uma instância de anexo para o formato de resposta.

        Args:
            anexo (Anexo): Instância do anexo que será convertida.

        Returns:
            dict[str, Any]: Dicionário contendo os principais dados do anexo.
        """
        return {
            "uuid": str(anexo.uuid),
            "nome": anexo.nome_original,
            "tipo": anexo.tipo,
            "tipo_mime": anexo.tipo_mime,
            "tamanho": anexo.tamanho_bytes,
            "url": anexo.url,
        }

    def _consulta_por_uuid(self, identificador: str) -> Anexo:
        """Consulta um anexo pelo seu identificador UUID.

        Realiza a busca de um anexo no banco de dados utilizando o UUID
        como chave de busca.

        Args:
            identificador (str): Identificador UUID do anexo que será
                consultado.

        Raises:
            AnexoArquivoError: Quando não existe um anexo com o UUID
            informado no sistema.

        Returns:
            Anexo: Instância do modelo Anexo correspondente ao UUID informado.
        """
        try:
            return Anexo.objects.get(uuid=identificador)
        except ObjectDoesNotExist as exc:
            raise AnexoArquivoError(
                title="Arquivo não encontrado.",
                detail="Arquivo não foi encontrado.",
            ) from exc

    @transaction.atomic
    def criar(
        self,
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
            nome_original (str): Nome original do arquivo enviado.
            tipo (str): Tipo do anexo conforme as opções definidas no modelo.
            tipo_mime (str): Tipo MIME do arquivo.
            tamanho_bytes (int): Tamanho do arquivo em bytes.
            usuario_id (int): Identificador do usuário responsável pela criação
            do anexo.

        Returns:
            dict[str, Any]: Dicionário contendo os dados do anexo criado:
            - uuid: Identificador único do anexo.
            - nome: Nome original do arquivo.
            - tipo: Tipo do anexo.
            - tipo_mime: Tipo MIME do arquivo.
            - tamanho: Tamanho do arquivo em bytes.
            - url: URL para acesso ao arquivo armazenado.
        Raises:
            UsuarioNaoEncontradoError: Quando o usuário com o ID informado
                não existe no sistema.
            AnexoArquivoError: Quando ocorre um erro durante o armazenamento
                do arquivo ou validação do anexo.
        """
        try:
            usuario = Usuario.objects.get(
                id=usuario_id,
            )
        except Usuario.DoesNotExist as exc:
            raise UsuarioNaoEncontradoError(
                title="Usuário não encontrado",
                detail="O usuário responsável pelo anexo não foi encontrado.",
            ) from exc
        anexo = Anexo.objects.create(
            nome_original=nome_original,
            tipo=tipo,
            tipo_mime=tipo_mime,
            tamanho_bytes=tamanho_bytes,
            arquivo=arquivo,
            criado_por=usuario,
        )
        return self._retorna_anexo_em_dicionario(anexo)

    def buscar_por_uuid(
        self,
        identificador: str,
    ) -> dict[str, Any]:
        """Busca um anexo pelo seu identificador UUID.

        Args:
            identificador (str): UUID do anexo que será consultado.

        Returns:
            dict[str, Any]: Dicionário contendo os dados do anexo encontrado.

        Raises:
            AnexoArquivoError: Se o anexo não for encontrado
        """
        anexo = self._consulta_por_uuid(identificador)
        return self._retorna_anexo_em_dicionario(anexo)

    def listar(
        self,
        tipo: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Lista os anexos, opcionalmente filtrados por tipo.

        Args:
            tipo (str | None): Tipo do anexo utilizado como filtro.
                Quando ``None``, retorna anexos de todos os tipos.

        Returns:
            dict[str, list[dict[str, Any]]]: Dicionário contendo a chave
            ``arquivos`` com a lista de anexos encontrados.
        """
        anexos = Anexo.objects.all()

        if tipo:
            anexos = anexos.filter(tipo=tipo)

        return {
            "arquivos": [
                self._retorna_anexo_em_dicionario(anexo) for anexo in anexos
            ]
        }

    @transaction.atomic
    def excluir(self, identificador: str) -> None:
        """Exclui um anexo do banco de dados.

        A operação é executada dentro de uma transação atômica.

        Args:
            identificador (str): Identificador UUID do anexo que será excluído.

        Raises:
            AnexoArquivoError: Se o anexo não for encontrado.
        """
        anexo = self._consulta_por_uuid(identificador)
        anexo.arquivo.delete(
            save=False,
        )
        anexo.delete()

    def buscar_para_download(self, identificador: str) -> dict[str, Any]:
        """Busca os dados necessários para realizar o download de um anexo.

        Args:
            identificador (str): Identificador UUID do anexo.

        Returns:
            Dicionário contendo o arquivo, nome original e tipo MIME.

        Raises:
            AnexoArquivoError: Se o anexo não for encontrado.
        """
        anexo = self._consulta_por_uuid(identificador)
        return {
            "arquivo": anexo.arquivo,
            "nome_original": anexo.nome_original,
            "tipo_mime": anexo.tipo_mime,
        }
