"""_summary_."""

import mimetypes
import uuid
from pathlib import Path
from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import QuerySet

from apps.core.constants import (
    MAPA_EXTENSOES_TIPO_ARQUIVO,
    TAMANHO_MAXIMO_ARQUIVO,
)
from apps.core.models.anexo import Anexo
from apps.core.repository.anexo_repository import AnexoRepository


class AnexoService:
    """Regras de negócio relacionadas ao armazenamento de arquivos."""

    def __init__(
        self,
        repository: AnexoRepository | None = None,
    ) -> None:
        """Inicializa o serviço com o repositório de anexos.

        Args:
            repository: Repositório utilizado para persistência e consulta
                dos anexos. Quando não informado, uma instância padrão de
                ``AnexoRepository`` é criada.
        """
        self.repository = repository or AnexoRepository()

    def enviar_arquivo(
        self, arquivo: UploadedFile, id_usuario: int
    ) -> dict[str, Any]:
        """Valida, armazena e registra um arquivo.

        O arquivo recebido é validado quanto ao nome, tamanho e extensão.
        Após as validações, seus metadados são preparados e o arquivo é
        persistido no armazenamento, sendo associado ao usuário informado.

        Args:
            arquivo: Arquivo que será validado e armazenado.
            id_usuario: Identificador do usuário responsável pelo envio
                do arquivo.

        Returns:
            Dicionário contendo os dados do anexo criado e persistido,
            incluindo seu identificador, nome, tipo, tipo MIME, tamanho
            e URL para acesso ao arquivo.

        Raises:
            ValueError: Se o arquivo for inválido, estiver vazio, possuir
            uma extensão não permitida ou ultrapassar o tamanho máximo
            permitido de 2 MB.
        """
        nome_arquivo, tamanho_bytes = self._validar_arquivo_recebido(
            arquivo,
        )
        if tamanho_bytes > TAMANHO_MAXIMO_ARQUIVO:
            raise ValueError(
                "O arquivo não pode ultrapassar 2 MB.",
            )

        tipo = self._validar_extensao_arquivo(nome_arquivo)

        return self._salvar(
            arquivo=arquivo,
            tipo=tipo,
            nome_original=nome_arquivo,
            tamanho_bytes=tamanho_bytes,
            id_usuario=id_usuario,
        )

    def buscar_por_id(
        self,
        identificador: str,
    ) -> Anexo | None:
        """Busca um anexo pelo seu identificador.

        Args:
            identificador: Identificador do anexo que será consultado.

        Returns:
            O anexo encontrado ou ``None`` caso não exista.
        """
        return self.repository.buscar_por_uuid(
            identificador,
        )

    def listar(
        self,
        *,
        tipo: str | None = None,
    ) -> QuerySet[Anexo]:
        """Lista os anexos, opcionalmente filtrados por tipo.

        Args:
            tipo: Tipo do anexo utilizado como filtro. Quando ``None``,
                retorna anexos de todos os tipos.

        Returns:
            QuerySet contendo os anexos encontrados.
        """
        return self.repository.listar(
            tipo=tipo,
        )

    @transaction.atomic
    def excluir(
        self,
        identificador: str,
    ) -> None:
        """Exclui um anexo e seu arquivo armazenado.

        Args:
            identificador: Identificador do anexo que será excluído.

        Raises:
            ValueError: Se o anexo não for encontrado.
        """
        arquivo = self.repository.buscar_por_uuid(
            identificador,
        )

        if arquivo is None:
            raise ValueError(
                "Arquivo não encontrado.",
            )

        arquivo.arquivo.delete(
            save=False,
        )

        self.repository.excluir(
            arquivo,
        )

    def obter_url(
        self,
        identificador: str,
    ) -> str:
        """Obtém a URL de acesso a um arquivo armazenado.

        Args:
            identificador: Identificador do anexo que será consultado.

        Returns:
            URL de acesso ao arquivo armazenado.

        Raises:
            ValueError: Se o anexo não for encontrado.
        """
        arquivo = self.repository.buscar_por_uuid(
            identificador,
        )

        if arquivo is None:
            raise ValueError(
                "Arquivo não encontrado.",
            )

        return arquivo.arquivo.url

    def _salvar(
        self,
        *,
        arquivo: UploadedFile,
        tipo: str,
        nome_original: str,
        tamanho_bytes: int,
        id_usuario: int,
    ) -> dict[str, Any]:
        """Prepara os metadados e persiste um arquivo.

        O nome original é normalizado para remover qualquer componente
        de caminho. Em seguida, é gerado um nome único para o arquivo
        que será armazenado. O tipo MIME é obtido a partir do arquivo
        enviado ou, caso não esteja disponível, inferido pela extensão
        do nome original.

        Args:
            arquivo: Arquivo que será armazenado.
            tipo: Tipo do anexo que será registrado.
            nome_original: Nome original validado do arquivo.
            tamanho_bytes: Tamanho validado do arquivo em bytes.
            id_usuario: Identificador do usuário responsável pela criação
            do anexo.

        Returns:
            Dicionário contendo os dados do anexo criado e persistido,
            incluindo seu identificador, nome, tipo, tipo MIME, tamanho
            e URL para acesso ao arquivo.
        """
        nome_original = Path(
            nome_original,
        ).name

        nome_arquivo = self._gerar_nome_arquivo(
            nome_original,
        )

        arquivo.name = nome_arquivo

        tipo_mime = (
            arquivo.content_type
            or mimetypes.guess_type(
                nome_original,
            )[0]
            or "application/octet-stream"
        )

        return self.repository.criar(
            nome_original=nome_original,
            tipo=tipo,
            tipo_mime=tipo_mime,
            tamanho_bytes=tamanho_bytes,
            arquivo=arquivo,
            usuario_id=id_usuario,
        )

    @staticmethod
    def _gerar_nome_arquivo(
        nome_original: str,
    ) -> str:
        """Gera um nome único preservando a extensão do arquivo.

        Args:
            nome_original: Nome original do arquivo.

        Returns:
            Nome composto por um UUID e pela extensão original.
        """
        extensao = Path(
            nome_original,
        ).suffix.lower()

        return f"{uuid.uuid4()}{extensao}"

    @staticmethod
    def _obter_extensao(
        nome_arquivo: str,
    ) -> str:
        """Obtém a extensão de um arquivo em letras minúsculas.

        Args:
            nome_arquivo: Nome do arquivo cuja extensão será obtida.

        Returns:
            Extensão do arquivo, incluindo o ponto inicial.
        """
        return Path(
            nome_arquivo,
        ).suffix.lower()

    @staticmethod
    def _validar_arquivo_recebido(
        arquivo: UploadedFile | None,
    ) -> tuple[str, int]:
        """Valida e retorna os metadados básicos de um arquivo.

        Args:
            arquivo: Arquivo recebido pela aplicação.

        Returns:
            Uma tupla contendo o nome do arquivo e seu tamanho em bytes.

        Raises:
            ValueError: Se o arquivo não for informado, não possuir nome,
                não permitir determinar seu tamanho ou estiver vazio.
        """
        if arquivo is None:
            raise ValueError(
                "Nenhum arquivo foi informado.",
            )

        nome = arquivo.name
        tamanho = arquivo.size

        if (nome is None) or (not nome):
            raise ValueError(
                "O arquivo precisa possuir um nome.",
            )

        if tamanho is None:
            raise ValueError(
                "Não foi possível determinar o tamanho do arquivo.",
            )

        if tamanho <= 0:
            raise ValueError(
                "Não é permitido enviar um arquivo vazio.",
            )

        return nome, tamanho

    def _validar_extensao_arquivo(self, nome_arquivo: str) -> str:
        """Valida a extensão do arquivo e identifica seu tipo.

        Obtém a extensão do nome do arquivo e verifica se ela está
        cadastrada no mapa de extensões permitidas. Quando a extensão
        é válida, retorna o tipo de arquivo correspondente.

        Args:
            nome_arquivo (str): Nome do arquivo que terá a extensão validada.

        Raises:
            ValueError: Quando a extensão do arquivo não está entre as
                extensões permitidas.

        Returns:
            str:  Tipo de arquivo correspondente à extensão informada.
        """
        extensao = self._obter_extensao(
            nome_arquivo,
        )
        try:
            return MAPA_EXTENSOES_TIPO_ARQUIVO[extensao]
        except KeyError as exc:
            raise ValueError(
                "O tipo de arquivo informado não é permitido.",
            ) from exc
