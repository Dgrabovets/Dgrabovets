"""Проект для карточки"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    """Репозиторий в списке проектов профиля"""

    repo: str
    section: str
    description: str
    # Подпись внизу карточки: язык из GitHub, а если его нет, значение из projects.json
    label: str
