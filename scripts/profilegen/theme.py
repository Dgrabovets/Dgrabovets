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
    accent: str
    language_colors: tuple[str, ...]


# Тёмная тема Aeternus Bordeaux, значения из tokens.json этой темы бренда, контраст текста выше 4.5:1
DARK = Theme(name="dark",
             background="#000000",
             card="#14040a",
             border="#63303f",
             foreground="#f6f1ef",
             muted="#c4b8bb",
             accent="#fa5f80",
             # Соседние цвета различаются по светлоте, иначе бордовые доли полосы сливаются
             language_colors=("#fa5f80", "#d4204f", "#f6f1ef", "#a82b62", "#c4b8bb"))

# Светлая тема Aeternus Bordeaux из того же tokens.json, для страницы GitHub в светлом оформлении
LIGHT = Theme(name="light",
              background="#f7f2ee",
              card="#ffffff",
              border="#e0d3ce",
              foreground="#17080c",
              muted="#55454a",
              accent="#650d27",
              language_colors=("#650d27", "#b5566c", "#17080c", "#d3a3ae", "#8e7278"))

THEMES = (DARK, LIGHT)
