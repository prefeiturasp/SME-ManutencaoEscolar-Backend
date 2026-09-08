"""Model referente as Unidades educacionais."""

from django.db import models

from apps.core.models.mixins import UUIDMixin
from apps.escola.models import ResponsavelUnidade
from apps.lote.models import Lote


class Unidadeeducacional(UUIDMixin):
    """Representa uma unidade escolar cadastrada no sistema EOL."""

    codigo_eol = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código identificador da escola no sistema EOL.",
    )
    nome = models.CharField(
        max_length=255,
        help_text="Nome da escola.",
    )
    diretoria_regional = models.ForeignKey(
        "escola.DiretoriaRegional",
        on_delete=models.PROTECT,
        related_name="escolas",
        help_text="Diretoria Regional de Educação da escola.",
    )
    tipo_escola = models.ForeignKey(
        "escola.TipoEscola",
        on_delete=models.PROTECT,
        related_name="escolas",
        help_text="Tipo da unidade escolar.",
    )
    subprefeitura = models.ForeignKey(
        "escola.Subprefeitura",
        on_delete=models.PROTECT,
        related_name="escolas",
        null=True,
        blank=True,
        help_text="Subprefeitura onde a escola está localizada.",
    )
    status = models.BooleanField(default=True)

    class Meta:
        ordering = (
            "-status",
            "nome",
        )
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"

    def __str__(self) -> str:
        return f"{self.codigo_eol} - {self.nome}"

    @property
    def responsaveis_atuais(self) -> models.QuerySet:
        """Retorna os responsáveis atualmente vinculados à unidade.

        Uma unidade educacional pode possuir até múltiplos responsáveis
        simultaneamente, cada um podendo exercer um cargo diferente.

        O vínculo atual é identificado por `data_fim` igual a `None`.

        Returns:
            QuerySet: Históricos dos responsáveis atualmente vinculados,
                com o responsável e o cargo carregados.
        """
        return self.historico_responsaveis.filter(
            ativo=True,
        ).select_related("responsavel", "cargo")

    @property
    def diretor_atual(self) -> ResponsavelUnidade | None:
        """Retorna o diretor atualmente vinculado à unidade.

        Procura entre os responsáveis atuais da unidade aquele que possui
        o cargo de diretor.

        Returns:
            ResponsavelUnidade | None: O diretor atual da unidade ou `None`
                quando não houver um responsável com cargo de diretor.
        """
        historico = (
            self.historico_responsaveis.filter(
                ativo=True,
                cargo__nome__iexact="DIRETOR DE ESCOLA",
            )
            .select_related("responsavel", "cargo")
            .first()
        )

        return historico.responsavel if historico else None

    @property
    def lote(self) -> Lote | None:
        """Retorna o lote ativo vinculado à Diretoria Regional da unidade.

        A unidade educacional obtém seu lote por meio da Diretoria Regional.
        Caso exista um vínculo com um lote ativo, retorna o objeto ``Lote``.
        Caso contrário, retorna ``None``.

        Returns:
            Lote | None: O lote ativo da Diretoria Regional ou ``None`` quando
            não houver lote ativo vinculado.
        """
        lote_diretoria = (
            self.diretoria_regional.vinculo_lote.filter(
                lote__status=True,
            )
            .select_related("lote")
            .first()
        )

        return lote_diretoria.lote if lote_diretoria else None


class DadosUnidadeEducacional(models.Model):
    """Armazena dados de contato e endereço de uma unidade educacional."""

    unidade_educacional = models.OneToOneField(
        "escola.Unidadeeducacional",
        on_delete=models.CASCADE,
        related_name="dados",
    )
    email = models.EmailField(
        blank=True,
        default="",
    )
    telefone = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )
    logradouro = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    numero = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )
    bairro = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    cep = models.CharField(
        max_length=8,
        blank=True,
        default="",
    )
    municipio = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    uf = models.CharField(
        max_length=2,
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = "Dados da Unidade Educacional"
        verbose_name_plural = "Dados das Unidades Educacionais"

    def __str__(self) -> str:
        return f"Dados de {self.unidade_educacional}"
