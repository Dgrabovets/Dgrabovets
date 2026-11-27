"""Палитра темы"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Цвета одной темы оформления"""

    name: str
    background: str
    card: str
    border: str
    foreground: str
    muted: str
    # Метки, рамка ранней стадии, блик и курсор. Тёмно-красный, для текста на чёрном слишком тёмный
    accent: str
    # Цветные подписи: названия разделов, языки на карточках, числа статистики
    label: str
    # Колонки света на карточках сервисов
    columns: str
    # Клетки графика активности на уровнях 0..4: пустой день серый, активные красные и заметно разные по светлоте
    heat_colors: tuple[str, ...]
    language_colors: tuple[str, ...]


# Тёмная тема: тёмно-красные метки и белые подписи. Баннер рисуется в бренде своим кроваво-красным, он здесь не участвует
DARK = Theme(name="dark",
             background="#000000",
             card="#000000",
             border="#5a0006",
             foreground="#ffffff",
             muted="#d1d7e0",
             accent="#b0101a",
             label="#ffffff",
             columns="#8b0000",
             heat_colors=("#484f58", "#a30f17", "#cc1f1f", "#e5322d", "#ff6a5e"),
             # Соседние цвета различаются по светлоте, иначе красные доли полосы сливаются
             language_colors=("#e5322d", "#ffffff", "#8b0000", "#8b949e", "#4d5561"))

# Светлая тема той же палитры на нейтральном фоне: кремовый рядом с красным выглядит розовым
LIGHT = Theme(name="light",
              background="#f6f5f5",
              card="#ffffff",
              border="#e2dcdb",
              foreground="#111111",
              muted="#4a4a4f",
              accent="#8b0000",
              label="#111111",
              columns="#8b0000",
              heat_colors=("#c4cad1", "#e07a76", "#cc4a44", "#8b0000", "#4a0004"),
              language_colors=("#b0101a", "#111111", "#e07a76", "#8c959f", "#d0d7de"))

THEMES = (DARK, LIGHT)
