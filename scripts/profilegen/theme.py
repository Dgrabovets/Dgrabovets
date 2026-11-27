"""Палитра темы"""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Theme:
    """Цвета одной темы оформления"""

    name: str
    background: str
    card: str
    border: str
    foreground: str
    muted: str
    accent: str
    language_colors: tuple[str, ...]


# Тёмная тема Aeternus Bordeaux, значения из tokens.json этой темы бренда, контраст текста выше 4.5:1
DARK = Theme(name="dark",
             background="#000000",
             card="#14040a",
             border="#2e181f",
             foreground="#d9c6c6",
             muted="#998a8e",
             accent="#d4637e",
             # Соседние цвета различаются по светлоте, иначе бордовые доли полосы сливаются
             language_colors=("#d4637e", "#a3173d", "#d9c6c6", "#7e1f4a", "#998a8e"))

# Светлая тема бренда пока черновик, поэтому под светлыми именами файлов лежит тёмное оформление
LIGHT = replace(DARK, name="light")

THEMES = (DARK, LIGHT)
