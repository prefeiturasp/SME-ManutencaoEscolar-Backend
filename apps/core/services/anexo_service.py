"""_summary_."""

import mimetypes
import uuid
from pathlib import Path

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import QuerySet

from apps.core.constants import TipoArquivo
from apps.core.models.anexo import Anexo
from apps.core.repository.anexo_repository import AnexoRepository


class AnexoService:
    """Regras de negócio relacionadas ao armazenamento de arquivos."""

    EXTENSOES_IMAGEM = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".bmp",
        ".tiff",
        ".svg",
    }

    EXTENSOES_ARQUIVO = {
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".csv",
        ".txt",
        ".zip",
        ".rar",
        ".7z",
    }

    TAMANHO_MAXIMO_ARQUIVO = 50 * 1024 * 1024
    TAMANHO_MAXIMO_IMAGEM = 10 * 1024 * 1024

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

    @transaction.atomic
    def enviar_imagem(
        self,
        arquivo: UploadedFile,
    ) -> Anexo:
        """Valida, armazena e registra uma imagem.

        Args:
            arquivo: Imagem que será validada e armazenada.

        Returns:
            O anexo criado após o armazenamento do arquivo.

        Raises:
            ValueError: Se o arquivo for inválido, estiver vazio, possuir
                uma extensão não permitida ou ultrapassar o tamanho máximo.
        """
        nome_arquivo, tamanho_bytes = self._validar_arquivo_recebido(
            arquivo,
        )

        extensao = self._obter_extensao(
            nome_arquivo,
        )

        if extensao not in self.EXTENSOES_IMAGEM:
            raise ValueError(
                "O arquivo informado não é uma imagem válida.",
            )

        if tamanho_bytes > self.TAMANHO_MAXIMO_IMAGEM:
            raise ValueError(
                "A imagem não pode ultrapassar 10 MB.",
            )

        return self._salvar(
            arquivo=arquivo,
            tipo=TipoArquivo.IMAGEM,
            nome_original=nome_arquivo,
            tamanho_bytes=tamanho_bytes,
        )

    @transaction.atomic
    def enviar_arquivo(
        self,
        arquivo: UploadedFile,
    ) -> Anexo:
        """Valida, armazena e registra um arquivo.

        Args:
            arquivo: Arquivo que será validado e armazenado.

        Returns:
            O anexo criado após o armazenamento do arquivo.

        Raises:
            ValueError: Se o arquivo for inválido, estiver vazio, possuir
                uma extensão não permitida ou ultrapassar o tamanho máximo.
        """
        nome_arquivo, tamanho_bytes = self._validar_arquivo_recebido(
            arquivo,
        )

        extensao = self._obter_extensao(
            nome_arquivo,
        )

        if extensao not in self.EXTENSOES_ARQUIVO:
            raise ValueError(
                "O tipo de arquivo informado não é permitido.",
            )

        if tamanho_bytes > self.TAMANHO_MAXIMO_ARQUIVO:
            raise ValueError(
                "O arquivo não pode ultrapassar 50 MB.",
            )

        return self._salvar(
            arquivo=arquivo,
            tipo=TipoArquivo.DOCUMENTO,
            nome_original=nome_arquivo,
            tamanho_bytes=tamanho_bytes,
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
    ) -> Anexo:
        """Prepara os metadados e persiste um arquivo.

        Args:
            arquivo: Arquivo que será armazenado.
            tipo: Tipo do anexo que será registrado.
            nome_original: Nome original validado do arquivo.
            tamanho_bytes: Tamanho validado do arquivo em bytes.

        Returns:
            O anexo criado e persistido.
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

        if nome is None:
            raise ValueError(
                "O arquivo precisa possuir um nome.",
            )

        if tamanho is None:
            raise ValueError(
                "Não foi possível determinar o tamanho do arquivo.",
            )

        if not nome:
            raise ValueError(
                "O arquivo precisa possuir um nome.",
            )

        if tamanho <= 0:
            raise ValueError(
                "Não é permitido enviar um arquivo vazio.",
            )

        return nome, tamanho
