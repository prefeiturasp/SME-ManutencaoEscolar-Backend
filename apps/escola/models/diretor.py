"""_summary_."""

from django.db import models

from apps.core.models.mixins import UUIDMixin


class Diretor(UUIDMixin):
    """Representa um servidor que exerce ou exerceu a função de diretor."""

    registro_funcional = models.CharField(
        max_length=7,
        unique=True,
        help_text="Registro funcional do servidor.",
    )
    nome = models.CharField(
        max_length=255,
        help_text="Nome do servidor.",
    )
    email = models.EmailField(
        max_length=254,
        blank=True,
        help_text="E-mail institucional do servidor.",
    )

    class Meta:
        ordering = ("nome",)
        verbose_name = "Diretor"
        verbose_name_plural = "Diretores"

    def __str__(self) -> str:
        return f"{self.registro_funcional} - {self.nome}"

    @property
    def escolas_atuais(self) -> models.QuerySet:
        """Retorna as escolas em que o diretor exerce a função atualmente.

        Um diretor pode exercer a função de diretor em mais de uma
        escola simultaneamente. Por isso, esta propriedade pode retornar
        zero, uma ou várias escolas por meio dos respectivos registros
        de histórico.

        Returns:
            QuerySet: QuerySet de históricos de vínculo atualmente ativos,
                com a unidade educacional carregada por `select_related`.
        """
        return self.historicos_escola.filter(
            data_fim__isnull=True
        ).select_related("unidade_educacional")


class HistoricoDiretorEscola(UUIDMixin):
    """Registra o período em que um diretor esteve vinculado a uma escola.

    Não pode existir duas linhas com o mesmo diretor + escola + data de início.
    Uma escola pode ter no máximo um histórico com data_fim = NULL.
    """

    diretor = models.ForeignKey(
        "escola.Diretor",
        on_delete=models.PROTECT,
        related_name="historicos_escola",
        help_text="Diretor vinculado à escola.",
    )
    unidade_educacional = models.ForeignKey(
        "escola.Unidadeeducacional",
        on_delete=models.PROTECT,
        related_name="historico_diretores",
        help_text="Escola em que o diretor exerceu a função.",
    )
    data_inicio = models.DateField(
        help_text="Data de início do exercício como diretor da escola.",
    )
    data_fim = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Data de término do exercício. "
            "Nulo significa que é o diretor atual."
        ),
    )

    class Meta:
        ordering = ("-data_inicio",)
        verbose_name = "Histórico de Diretor da Escola"
        verbose_name_plural = "Históricos de Diretores das Escolas"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "diretor",
                    "unidade_educacional",
                    "data_inicio",
                ),
                name="unique_historico_diretor_escola_inicio",
            ),
            models.UniqueConstraint(
                fields=("unidade_educacional",),
                condition=models.Q(data_fim__isnull=True),
                name="unique_diretor_atual_por_escola",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(data_fim__isnull=True)
                    | models.Q(data_fim__gte=models.F("data_inicio"))
                ),
                name="historico_diretor_data_fim_maior_inicio",
            ),
        ]
        indexes = [
            models.Index(
                fields=("unidade_educacional", "data_fim"),
                name="hist_dir_escola_fim_idx",
            ),
            models.Index(
                fields=("diretor", "data_fim"),
                name="hist_dir_diretor_fim_idx",
            ),
        ]

    def __str__(self) -> str:
        periodo = (
            f"{self.data_inicio:%d/%m/%Y} - {self.data_fim:%d/%m/%Y}"
            if self.data_fim
            else f"{self.data_inicio:%d/%m/%Y} - atual"
        )
        return (
            f"{self.unidade_educacional.codigo_eol} - "
            f"{self.diretor.nome} ({periodo})"
        )

    @property
    def atual(self) -> bool:
        """Indica se o histórico representa o vínculo atual.

        Um histórico é considerado atual quando não possui uma data
        de encerramento. O campo `data_fim` com valor `None` representa
        que o vínculo permanece vigente.

        Returns:
            bool: `True` quando o vínculo está vigente; `False` quando
                o vínculo já foi encerrado.
        """
        return self.data_fim is None
