"""Model dos responsáveis pela Unidade Educacional."""

from __future__ import annotations

from django.db import models

from apps.core.models.mixins import BaseModel


class ResponsavelUnidade(BaseModel):
    """Representa um servidor que exerce responsabilidade em uma unidade.

    O servidor é identificado pelo registro funcional e pode possuir
    vínculos com uma ou mais unidades educacionais ao longo do tempo.
    """

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
        default="",
        help_text="E-mail institucional do servidor.",
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Telefone de contato do servidor.",
    )
    celular = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Celular de contato do servidor.",
    )

    esta_afastado = models.BooleanField(default=False)

    class Meta:
        ordering = ("nome",)
        verbose_name = "Responsável da Unidade"
        verbose_name_plural = "Responsáveis das Unidades"

    def __str__(self) -> str:
        return f"{self.registro_funcional} - {self.nome}"

    @property
    def escolas_atuais(self) -> models.QuerySet:
        """Retorna os vínculos atuais do responsável com unidades educacionais.

        Um responsável pode exercer uma função em mais de uma unidade
        educacional simultaneamente. Por isso, a propriedade pode retornar
        zero, uma ou várias unidades.

        Returns:
            QuerySet: Históricos de responsabilidade atualmente ativos,
                com a unidade educacional carregada.
        """
        return self.historicos_unidade.filter(
            ativo=True,
        ).select_related("unidade_educacional")


class HistoricoResponsavel(BaseModel):
    """Representa o vínculo de um responsável com uma unidade e cargo."""

    responsavel = models.ForeignKey(
        "escola.ResponsavelUnidade",
        on_delete=models.PROTECT,
        related_name="historicos_unidade",
        help_text="Responsável vinculado à unidade educacional.",
    )
    unidade_educacional = models.ForeignKey(
        "escola.Unidadeeducacional",
        on_delete=models.PROTECT,
        related_name="historico_responsaveis",
        help_text="Unidade educacional onde o responsável exerce a função.",
    )
    cargo = models.ForeignKey(
        "usuarios.CargoEOL",
        on_delete=models.PROTECT,
        related_name="historicos_responsaveis",
        help_text="Cargo exercido pelo responsável na unidade.",
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Indica se o responsável está atualmente vinculado.",
    )

    class Meta:
        ordering = ("-atualizado_em",)
        verbose_name = "Histórico de Responsável da Unidade"
        verbose_name_plural = "Históricos de Responsáveis das Unidades"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "responsavel",
                    "unidade_educacional",
                    "cargo",
                ),
                name="unique_resp_unidade_cargo",
            ),
        ]
        indexes = [
            models.Index(
                fields=("unidade_educacional", "ativo"),
                name="hist_resp_unidade_ativo_idx",
            ),
            models.Index(
                fields=("responsavel", "ativo"),
                name="hist_resp_resp_ativo_idx",
            ),
            models.Index(
                fields=("cargo", "ativo"),
                name="hist_resp_cargo_ativo_idx",
            ),
        ]

    def __str__(self) -> str:
        status = "ativo" if self.ativo else "inativo"
        return (
            f"{self.unidade_educacional.codigo_eol} - "
            f"{self.responsavel.nome} - "
            f"{self.cargo.nome} ({status})"
        )

    @property
    def atual(self) -> bool:
        """Indica se o vínculo do responsável está ativo.

        Returns:
            bool: True quando o vínculo está ativo e False quando está inativo.
        """
        return self.ativo
