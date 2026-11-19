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


# Палитра дашборда Unified Band: почти чёрный фон, тёплый серый текст, зелёный акцент, контраст текста не ниже 4.5:1
DARK = Theme(name="dark",
             background="#060606",
             card="#0C0C0C",
             border="#2A2A27",
             foreground="#F3F2EE",
             muted="#8D8B84",
             accent="#5FE08A",
             language_colors=("#5FE08A", "#6CB4F0", "#B07CF0", "#F0A050", "#E0709A"))

# Светлая палитра того же дашборда: светло-серый фон, белые карточки и глубокий зелёный
LIGHT = Theme(name="light",
              background="#F5F5F3",
              card="#FFFFFF",
              border="#DEDCD6",
              foreground="#1D1C1A",
              muted="#6E6C66",
              accent="#2F7D3B",
              language_colors=("#2F7D3B", "#1D6FA5", "#7A4FC0", "#B36B12", "#B03A78"))

THEMES = (DARK, LIGHT)
