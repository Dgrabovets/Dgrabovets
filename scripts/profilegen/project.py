"""Проект для карточки"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    """Репозиторий в списке проектов профиля"""

    repo: str
    section: str
    description: str
    language: str
    stars: int
