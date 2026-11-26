"""Текст в виде контуров: GitHub не подгружает веб-шрифты в SVG"""

import json
from functools import lru_cache
from pathlib import Path

from .font_enum import FontEnum

# Контуры символов, файл пересобирается скриптом `scripts/extract_glyphs.py`
GLYPHS_PATH = Path(__file__).with_name("glyphs.json")

# Чем заменяется буква из внешних данных, которой нет в таблице
FALLBACK_SYMBOL = "?"


# region Helpers
@lru_cache
def _fonts() -> dict:
    """Читает таблицу контуров

    Returns:
        Словарь «начертание → размер em и символы»
    """
    return json.loads(GLYPHS_PATH.read_text(encoding="utf-8"))["fonts"]


def _glyph(font: FontEnum, symbol: str) -> tuple[int, str]:
    """Ищет символ в начертании

    Args:
        font: Начертание
        symbol: Один символ

    Returns:
        Ширина и контур в единицах шрифта

    Raises:
        ValueError: Символа нет в таблице
    """
    glyphs = _fonts()[font.value]["glyphs"]

    if symbol not in glyphs:
        raise ValueError(f"В шрифте {font.value} нет символа {symbol!r}, добавь его в scripts/extract_glyphs.py")

    return glyphs[symbol]


def _scale(font: FontEnum, size: float) -> float:
    """Считает масштаб из единиц шрифта в пиксели

    Args:
        font: Начертание
        size: Размер шрифта в пикселях

    Returns:
        Множитель
    """
    return size / _fonts()[font.value]["unitsPerEm"]
# endregion Helpers


# region Text
def printable(text: str, font: FontEnum) -> str:
    """Заменяет буквы, которых нет в таблице: чужие данные не должны ронять сборку

    Args:
        text: Строка из GitHub
        font: Начертание

    Returns:
        Строка, которую можно нарисовать
    """
    glyphs = _fonts()[font.value]["glyphs"]

    return "".join(symbol if symbol in glyphs else FALLBACK_SYMBOL for symbol in text)


def text_width(text: str,
               font: FontEnum,
               size: float,
               spacing: float = 0.0) -> float:
    """Измеряет ширину строки

    Args:
        text: Строка
        font: Начертание
        size: Размер шрифта в пикселях
        spacing: Добавка между буквами в пикселях

    Returns:
        Ширина в пикселях
    """
    scale = _scale(font, size)

    return sum(_glyph(font, symbol)[0] * scale for symbol in text) + spacing * max(len(text) - 1, 0)


def text_path(text: str,
              x: float,
              y: float,
              font: FontEnum,
              size: float,
              fill: str,
              spacing: float = 0.0) -> str:
    """Рисует строку контурами

    Args:
        text: Строка
        x: Левый край
        y: Базовая линия
        font: Начертание
        size: Размер шрифта в пикселях
        fill: Цвет
        spacing: Добавка между буквами в пикселях

    Returns:
        SVG-группа с контурами букв
    """
    scale = _scale(font, size)
    cursor = 0.0
    paths = ""

    # shortcut: без кернинга, добавить, если буквы в пропорциональном шрифте встанут неровно
    for symbol in text:
        advance, outline = _glyph(font, symbol)

        if outline:
            paths += f'<path transform="translate({cursor:.0f})" d="{outline}"/>'

        cursor += advance + spacing / scale

    return f'<g transform="translate({x:g} {y:g}) scale({scale:g})" fill="{fill}">{paths}</g>'
# endregion Text
