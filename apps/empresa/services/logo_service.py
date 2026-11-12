"""Serviços para a logo das empresas."""

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from apps.core.services.anexo_service import AnexoService
from apps.empresa.repository.logo_repository import LogoEmpresaRepository
from apps.usuarios.models import Usuario


class LogoEmpresaService:
    """Orquestra o upload e a persistência da logo de uma empresa."""

    def __init__(
        self,
        repository: LogoEmpresaRepository | None = None,
        anexo_service: AnexoService | None = None,
    ) -> None:
        """Inicializa o serviço com o repositório e o serviço de anexos.

        Args:
            repository: Repositório da logo. Quando não informado, uma
                instância padrão de ``LogoEmpresaRepository`` é criada.
            anexo_service: Serviço de anexos do core, responsável pelas
                validações de arquivo. Quando não informado, uma instância
                padrão de ``AnexoService`` é criada.
        """
        self.repository = repository or LogoEmpresaRepository()
        self.anexo_service = anexo_service or AnexoService()

    @transaction.atomic
    def sincronizar(
        self,
        empresa_id: int,
        logo: UploadedFile | None,
        usuario: Usuario | None = None,
    ) -> str | None:
        """Substitui ou remove a logo da empresa.

        Args:
            empresa_id: ID da empresa dona da logo.
            logo: Novo arquivo de imagem ou ``None`` para remover a logo.
            usuario: Usuário responsável pela operação.

        Returns:
            URL da nova logo ou ``None`` quando a logo foi removida.

        Raises:
            AnexoArquivoError: Se o arquivo for inválido (vazio, acima do
                tamanho máximo ou com extensão não permitida).
            UsuarioNaoEncontradoError: Se o usuário não existir.
        """
        if logo is None:
            self.repository.remover(empresa_id)
            return None

        dados_anexo = self.anexo_service.validar_e_preparar_anexo(
            arquivo=logo,
            id_usuario=usuario.id if usuario is not None else None,
        )
        nova_logo = self.repository.substituir(
            empresa_id, dados_anexo, usuario
        )
        return str(nova_logo["arquivo_url"])

    def obter_url(self, empresa_id: int) -> str | None:
        """Obtém a URL da logo atual da empresa.

        Args:
            empresa_id: ID da empresa dona da logo.

        Returns:
            URL da logo ou ``None`` se a empresa não possuir logo.
        """
        return self.repository.obter_url(empresa_id)
