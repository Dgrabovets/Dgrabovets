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
    # Бордовые колонки света на карточках сервисов, для текста слишком тёмный
    columns: str
    language_colors: tuple[str, ...]


# Тёмная тема Aeternus Bordeaux, значения из tokens.json этой темы бренда, контраст текста выше 4.5:1
DARK = Theme(name="dark",
             background="#000000",
             card="#000000",
             border="#7a1c35",
             foreground="#ffffff",
             muted="#d1d7e0",
             accent="#ff5c7f",
             columns="#d4204f",
             # Соседние цвета различаются по светлоте, иначе бордовые доли полосы сливаются
             language_colors=("#ff5c7f", "#d4204f", "#ffffff", "#a82b62", "#d1d7e0"))

# Светлая тема Aeternus Bordeaux из того же tokens.json, для страницы GitHub в светлом оформлении
LIGHT = Theme(name="light",
              background="#f7f2ee",
              card="#ffffff",
              border="#e0d3ce",
              foreground="#17080c",
              muted="#55454a",
              accent="#650d27",
              columns="#8e1b3a",
              language_colors=("#650d27", "#b5566c", "#17080c", "#d3a3ae", "#8e7278"))

THEMES = (DARK, LIGHT)
