"""Виды проектов профиля"""

from enum import Enum


class ProjectKindEnum(str, Enum):
    """Вид проекта задаёт анимацию карточки, значение равно полю `kind` в `projects.json`"""

    BACKEND = "backend"
    APP = "app"
    TOOL = "tool"
    EARLY = "early"
