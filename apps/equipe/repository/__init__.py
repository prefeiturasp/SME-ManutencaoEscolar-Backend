"""Repositórios do domínio Equipe."""

from apps.equipe.repository.equipe_repository import EquipeRepository
from apps.equipe.repository.profissional_repository import (
    ProfissionalEquipeRepository,
)

__all__ = ["EquipeRepository", "ProfissionalEquipeRepository"]
