"""Начертания шрифтов бренда"""

from enum import Enum


class FontEnum(str, Enum):
    """Начертание, значение равно ключу в `glyphs.json`"""

    MONO_MEDIUM = "mono-500"
    MONO_BOLD = "mono-700"
    SANS_REGULAR = "sans-400"
