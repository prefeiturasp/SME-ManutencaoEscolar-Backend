"""Mixins e modelo base para padronizar comportamentos dos modelos Django.

Este módulo fornece componentes reutilizáveis para adicionar aos modelos:

- identificação por UUID;
- informações de criação e atualização;
- auditoria do usuário responsável pelas operações;
- exclusão lógica (soft delete) e restauração;
- armazenamento e acesso a arquivos anexados.

Os mixins são abstratos e não criam tabelas próprias no banco de dados.
"""

import uuid
from typing import Any

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.constants import TipoArquivo
from apps.core.storage import get_private_storage


class CustomManager(models.Manager):
    """
    Gerenciador que retorna apenas registros que não foram excluídos.

    Este gerenciador é utilizado pelo :class:`SoftDeleteMixin` como o
    gerenciador padrão (`objects`). Registros cujo campo ``deletado_em``
    esteja preenchido são automaticamente excluídos dos querysets.

    Para consultar também os registros excluídos logicamente, utilize o
    gerenciador ``dm_objects`` disponibilizado pelo
    :class:`SoftDeleteMixin`.
    """

    def get_queryset(self) -> models.QuerySet:
        """Retorna os registros que não possuem data de exclusão.

        Returns:
            models.QuerySet: Queryset filtrado para conter somente registros
            cujo campo ``deletado_em`` seja ``None``.
        """
        return super().get_queryset().filter(deletado_em=None)


class UUIDMixin(models.Model):
    """
    Adiciona um UUID como identificador primário do modelo.

    O UUID é gerado automaticamente na criação do registro e não pode ser
    alterado.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CriacaoMixin(models.Model):
    """
    Adiciona informações de auditoria relacionadas à criação.

    Registra automaticamente a data e hora em que o objeto foi criado e
    permite associá-lo ao usuário responsável pela criação.
    """

    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_criado",
    )

    class Meta:
        abstract = True


class AtualizacaoMixin(models.Model):
    """
    Adiciona informações de auditoria relacionadas à atualização.

    A data e hora da última atualização são atualizadas automaticamente pelo
    Django sempre que o objeto é salvo. O usuário responsável pela alteração
    pode ser registrado por meio do campo ``atualizado_por``.
    """

    atualizado_em = models.DateTimeField(auto_now=True)
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_atualizado",
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    Adiciona exclusão lógica e restauração de registros.

    A exclusão lógica não remove o registro do banco de dados. Em vez disso,
    preenche ``deletado_em`` com a data e hora da exclusão e, opcionalmente,
    registra o usuário responsável em ``deletado_por``.

    O gerenciador ``objects`` oculta automaticamente os registros excluídos.
    O gerenciador ``dm_objects`` permite consultar todos os registros,
    incluindo os excluídos logicamente.
    """

    deletado_em = models.DateTimeField(
        "Deletado em", default=None, null=True, blank=True
    )
    deletado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_deletado",
    )

    objects = CustomManager()
    dm_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(
        self,
        usuario: Any | None = None,
    ) -> tuple[int, dict[str, int]]:
        """
        Realiza a exclusão lógica do registro.

        O registro permanece armazenado no banco de dados, mas passa a ser
        ocultado pelo gerenciador padrão ``objects``.

        Args:
            usuario: Usuário responsável pela exclusão. Pode ser ``None``
                quando a operação não estiver associada a um usuário.

        Returns:
            tuple[int, dict[str, int]]: Quantidade de registros afetados e
            um dicionário contendo o label do modelo e a quantidade afetada,
            seguindo o formato utilizado pelo método ``delete()`` do Django.
        """
        self.deletado_em = timezone.now()
        self.deletado_por = usuario
        self.save(update_fields=["deletado_em", "deletado_por"])
        return 1, {self._meta.label: 1}

    def delete(
        self, using: str | None = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """
        Remove fisicamente o registro do banco de dados.

        Diferentemente de :meth:`soft_delete`, este método executa a exclusão
        física padrão do Django. O registro e suas relações sujeitas à
        política de exclusão configurada podem ser removidos definitivamente.

        Args:
            using: Alias da conexão do banco de dados a ser utilizada.
            keep_parents: Indica se os registros dos modelos-pai devem ser
                preservados em uma herança multi-tabela.

        Returns:
            tuple[int, dict[str, int]]: Quantidade de objetos removidos e
            quantidade de objetos removidos por tipo de modelo.
        """
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """
        Restaura um registro excluído logicamente.

        Define ``deletado_em`` como ``None``, fazendo com que o registro volte
        a aparecer nas consultas realizadas por meio do gerenciador
        ``objects``.

        O campo ``deletado_por`` não é alterado durante a restauração, o que
        preserva a informação sobre quem realizou a última exclusão lógica.
        """
        self.deletado_em = None
        self.save(update_fields=["deletado_em"])


class AuditMixin(
    CriacaoMixin,
    AtualizacaoMixin,
    SoftDeleteMixin,
):
    """
    Combina os recursos de criação, atualização e exclusão lógica.

    Fornece, em um único mixin, os campos e comportamentos necessários para
    registrar:

    - quando e por quem o registro foi criado;
    - quando e por quem o registro foi atualizado;
    - quando e por quem o registro foi excluído logicamente;
    - restauração de registros excluídos.
    """

    class Meta:
        abstract = True


class BaseModel(UUIDMixin, AuditMixin):
    """
    Modelo base para entidades persistidas da aplicação.

    Combina identificação por UUID, auditoria de criação e atualização e
    exclusão lógica.

    Modelos podem herdar desta classe para obter automaticamente
    esses recursos sem precisar declarar os campos individualmente.
    """

    class Meta:
        abstract = True


class AnexoMixin(BaseModel):
    """
    Adiciona suporte a arquivos anexados armazenados em storage privado.

    Além dos recursos fornecidos por :class:`BaseModel`, disponibiliza campos
    para armazenar informações sobre o arquivo original, seu tipo, MIME e
    tamanho.

    O arquivo é armazenado utilizando o storage retornado por
    :func:`get_private_storage`, em uma estrutura de diretórios organizada
    por ano, mês e dia.
    """

    nome_original = models.CharField(
        max_length=255,
    )

    arquivo = models.FileField(
        upload_to="arquivos/%Y/%m/%d/",
        storage=get_private_storage,
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoArquivo.choices,
    )

    tipo_mime = models.CharField(
        max_length=150,
        blank=True,
    )

    tamanho_bytes = models.PositiveBigIntegerField(
        default=0,
    )

    class Meta:
        abstract = True

    @property
    def nome_bucket(self) -> str:
        """
        Retorna o caminho/nome do objeto no storage.

        Apesar do nome da propriedade, o valor retornado não é o nome do
        bucket. Ele corresponde ao valor de ``arquivo.name``, que identifica
        o caminho e o nome do objeto dentro do storage.

        Returns:
            str: Caminho e nome do objeto armazenado.

        Raises:
            ValueError: Se nenhum arquivo tiver sido associado ao objeto.
        """
        if not self.arquivo.name:
            raise ValueError("O nome do arquivo não está definido.")
        return self.arquivo.name

    @property
    def url(self) -> str:
        """Retorna a URL de acesso ao arquivo.

        A URL é obtida diretamente do storage configurado no campo
        :attr:`arquivo`. Para storages privados, ela pode ser uma URL
        assinada ou temporária, dependendo da implementação do storage.

        Returns:
            str: URL utilizada para acessar o arquivo armazenado.
        """
        return self.arquivo.url
