"""Modelos do domínio Profissional."""

from django.db import models
from django.db.models.functions import Lower

from apps.cargo.models import Cargo
from apps.core.models.mixins import AnexoMixin, BaseModel
from apps.profissional.constants import ProfissionalErrorMessages


class Profissional(BaseModel):
    """Representa o cadastro de um profissional."""

    nome = models.CharField(max_length=255)
    rg = models.CharField(max_length=20)
    cpf = models.CharField(max_length=11)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"
        ordering = ["-status", "-id"]
        indexes = [
            models.Index(fields=["rg"]),
            models.Index(fields=["cpf"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["cpf"],
                condition=models.Q(deletado_em__isnull=True),
                name="profissional_cpf_unico",
                violation_error_message=ProfissionalErrorMessages.PROFISSIONAL_CPF_JA_CADASTRADO,
            ),
            models.UniqueConstraint(
                fields=["rg"],
                condition=models.Q(deletado_em__isnull=True),
                name="profissional_rg_unico",
                violation_error_message=ProfissionalErrorMessages.PROFISSIONAL_RG_JA_CADASTRADO,
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nome} - {self.cpf}"


class FuncaoProfissional(BaseModel):
    """Representa uma função exercida por um profissional."""

    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.CASCADE,
        related_name="funcoes",
    )
    profissional = models.ForeignKey(
        Profissional,
        on_delete=models.CASCADE,
        related_name="funcoes",
    )

    class Meta:
        verbose_name = "Função do Profissional"
        verbose_name_plural = "Funções dos Profissionais"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["cargo", "profissional"],
                condition=models.Q(deletado_em__isnull=True),
                name="funcao_profissional_cargo_unico",
                violation_error_message=ProfissionalErrorMessages.FUNCAO_PROFISSIONAL_JA_CADASTRADA,
            )
        ]

    def __str__(self) -> str:
        return f"{self.profissional.nome} - {self.cargo.nome}"


class DocumentoExigidoFuncao(BaseModel):
    """Documento que o cargo exigia quando foi vinculado ao profissional.

    É uma cópia (snapshot) dos documentos do cargo no momento do vínculo.
    Mudanças posteriores no cadastro do cargo não alteram estes registros;
    eles só são recriados quando o cargo é vinculado novamente.
    """

    funcao_profissional = models.ForeignKey(
        FuncaoProfissional,
        on_delete=models.CASCADE,
        related_name="documentos_exigidos",
    )
    nome = models.CharField(max_length=255)
    ordem = models.PositiveSmallIntegerField(
        help_text="Posição do documento no cargo no momento do vínculo."
    )

    class Meta:
        verbose_name = "Documento exigido da Função profissional"
        verbose_name_plural = "Documentos exigidos das Funções profissionais"
        ordering = ["ordem", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["funcao_profissional", "ordem"],
                condition=models.Q(deletado_em__isnull=True),
                name="documento_exigido_funcao_ordem_unica",
            ),
            models.UniqueConstraint(
                Lower("nome"),
                "funcao_profissional",
                condition=models.Q(deletado_em__isnull=True),
                name="documento_exigido_funcao_nome_unico",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nome} - {self.funcao_profissional}"


class DocumentoFuncaoProfissional(AnexoMixin):
    """Representa um documento exigido para uma função profissional."""

    funcao_profissional = models.ForeignKey(
        FuncaoProfissional,
        on_delete=models.CASCADE,
        related_name="documentos",
    )
    arquivo = models.FileField(
        upload_to="profissionais/anexos_funcoes_profissionais/"
    )
    documento_exigido = models.ForeignKey(
        DocumentoExigidoFuncao,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="anexos",
        help_text="Documento exigido da função que este arquivo comprova.",
    )

    class Meta:
        verbose_name = "Documento da Função profissional"
        verbose_name_plural = "Documentos das Funções profissionais"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.nome_original} - {self.funcao_profissional}"
