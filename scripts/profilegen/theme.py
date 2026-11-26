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


# Тёмная тема бренда Aeternus, значения из tokens.json бренда, контраст текста выше 4.5:1
DARK = Theme(name="dark",
             background="#000000",
             card="#03100a",
             border="#232a25",
             foreground="#f3f2ee",
             muted="#a4a69f",
             accent="#5fe08a",
             language_colors=("#5fe08a", "#2fd4c0", "#1c6b47", "#a4a69f", "#f3f2ee"))

# Светлая тема бренда пока черновик, поэтому под светлыми именами файлов лежит тёмное оформление
LIGHT = replace(DARK, name="light")

THEMES = (DARK, LIGHT)
