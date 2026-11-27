"""Строка легенды анимаций карточек"""

from dataclasses import dataclass

from .project_kind_enum import ProjectKindEnum


@dataclass(frozen=True)
class LegendEntry:
    """Что значит анимация карточки"""

    kind: ProjectKindEnum
    title: str
    # Название анимации
    name: str
    # Почему именно она, для альтернативного текста картинки
    meaning: str
