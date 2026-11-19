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


# Палитра подобрана по ui-ux-pro-max: slate и зелёный акцент, контраст текста не ниже 4.5:1
DARK = Theme(name="dark",
             background="#0F172A",
             card="#1B2336",
             border="#475569",
             foreground="#F8FAFC",
             muted="#94A3B8",
             accent="#22C55E",
             language_colors=("#22C55E", "#38BDF8", "#A78BFA", "#F59E0B", "#F472B6"))

# Светлая бумажная палитра: беж и хвойный зелёный
LIGHT = Theme(name="light",
              background="#FBF7EE",
              card="#EFE6D2",
              border="#D9CFB8",
              foreground="#2B2A24",
              muted="#6B6554",
              accent="#3F6B3A",
              language_colors=("#3F6B3A", "#1D6FA5", "#6D4FB3", "#A8650D", "#B03A78"))

THEMES = (DARK, LIGHT)
