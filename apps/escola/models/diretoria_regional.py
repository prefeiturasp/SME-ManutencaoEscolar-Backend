"""Modelos da aplicação Core."""

from django.db import models


class DiretoriaRegional(models.Model):
    """Modelo que representa uma Diretoria Regional de Educação (DRE)."""

    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=255)
    abreviacao = models.CharField(max_length=50)

    class Meta:
        ordering = ("nome",)
        verbose_name = "Diretoria Regional"
        verbose_name_plural = "Diretorias Regionais"

    def __str__(self) -> str:
        return f"{self.abreviacao} - {self.nome}"

    @property
    def nome_curto(self) -> str:
        """Retorna o nome da Diretoria regional  de forma abreviada."""
        if self.nome and self.nome.startswith(
            "DIRETORIA REGIONAL DE EDUCACAO"
        ):
            return self.nome.replace(
                "DIRETORIA REGIONAL DE EDUCACAO", "DRE"
            ).strip()
        return self.nome
