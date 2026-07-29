"""Modelos da aplicação Core."""

from django.db import models


class DiretoriaRegional(models.Model):
    """Modelo que representa uma Diretoria Regional de Educação (DRE)."""

    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=255)
    abreviacao = models.CharField(max_length=50)

    class Meta:
        db_table = "diretoria_regional"
        verbose_name = "Diretoria Regional"
        verbose_name_plural = "Diretorias Regionais"

    def __str__(self) -> str:
        return f"{self.abreviacao} - {self.nome}"
