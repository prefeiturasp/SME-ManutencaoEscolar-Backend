"""
Repositório responsável pelo acesso aos anexos da aplicação.

Este módulo centraliza as operações de persistência e consulta de anexos,
incluindo criação, busca, listagem, download e exclusão de arquivos.

"""

from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import ObjectDoesNotExist

from apps.core.exceptions import AnexoArquivoError
from apps.core.models import Anexo
from apps.usuarios.exceptions import UsuarioNaoEncontradoError
from apps.usuarios.models.usuario import Usuario


class AnexoRepository:
    """
    Centraliza o acesso e as operações de persistência de anexos.

    O repositório encapsula o acesso ao modelo :class:`Anexo`, evitando que as
    camadas superiores precisem lidar diretamente com consultas e operações de
    persistência relacionadas aos arquivos.

    As operações disponibilizadas incluem:

    * criação de anexos;
    * busca de um anexo pelo UUID;
    * listagem de anexos, com filtro opcional por tipo;
    * preparação dos dados necessários para download;
    * exclusão do arquivo armazenado e do respectivo registro.
    """

    model = Anexo

    def _retorna_anexo_em_dicionario(self, anexo: Anexo) -> dict[str, Any]:
        """Transforma uma instância de anexo para o formato de resposta.

        Args:
            anexo (Anexo): Instância do anexo que será convertida.

        Returns:
            dict[str, Any]: Dicionário contendo os principais dados do anexo.
                - ``uuid``: Identificador único do anexo como string.
                - ``nome``: Nome original do arquivo.
                - ``tipo``: Tipo do arquivo.
                - ``tipo_mime``: Tipo MIME do arquivo.
                - ``tamanho``: Tamanho do arquivo em bytes.
                - ``url``: URL de acesso ao arquivo.
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

        O usuário responsável é consultado antes da criação do anexo.
        A operação é executada dentro de uma transação atômica para garantir
        que as operações de banco de dados realizadas pelo método sejam
        confirmadas ou revertidas.

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
            dict[str, Any]: Dados do anexo encontrado, incluindo UUID, nome,
                tipo, tipo MIME, tamanho e URL de acesso.

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

        A consulta pode ser opcionalmente filtrada pelo tipo do anexo.
        Quando nenhum tipo é informado, todos os anexos retornados pelo
        gerenciador padrão do modelo são incluídos.

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

        Primeiro, o arquivo associado ao anexo é removido do storage.
        Em seguida, o registro do anexo é removido do banco de dados.

        A operação é executada dentro de uma transação atômica para as
        operações de banco de dados. A remoção do arquivo no storage é
        realizada separadamente por meio do campo ``arquivo``.

        Args:
            identificador (str): Identificador UUID do anexo que será excluído.

        Raises:
            AnexoArquivoError: Se o anexo não for encontrado com o UUID
                informado.
        """
        anexo = self._consulta_por_uuid(identificador)
        anexo.arquivo.delete(
            save=False,
        )
        anexo.delete()

    def buscar_para_download(self, identificador: str) -> dict[str, Any]:
        """Busca os dados necessários para realizar o download de um anexo.

        Diferentemente de :meth:`buscar_por_uuid`, este método não retorna a
        URL do arquivo. Ele retorna diretamente a referência ao arquivo
        armazenado, juntamente com os metadados necessários para construir uma
        resposta de download.

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
