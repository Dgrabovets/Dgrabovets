"""Отрисовка SVG: баннер, карточки проектов и статистика"""

import textwrap
from xml.sax.saxutils import escape

from .profile_stats import ProfileStats
from .project import Project
from .theme import Theme

# Шрифты без внешней загрузки: GitHub не подгружает веб-шрифты в SVG
MONO_FONT = "'JetBrains Mono','IBM Plex Mono',Consolas,'Courier New',monospace"
SANS_FONT = "'IBM Plex Sans','Segoe UI',Arial,sans-serif"

# Размер карточки проекта
CARD_WIDTH = 424
CARD_HEIGHT = 112

# Сколько символов описания помещается в строку карточки при шрифте 13px
DESCRIPTION_LINE_CHARS = 52

# Сколько строк описания показывается, остальное заменяется многоточием
DESCRIPTION_LINES = 2

# Размер клетки графика активности и зазор между клетками
HEAT_CELL = 16
HEAT_GAP = 3

# Прозрачность клеток графика на уровнях 0..4, от пустой до самой активной
HEAT_ALPHAS = (0.35, 0.3, 0.55, 0.8, 1.0)

# Верхние границы числа вкладов за день для уровней 1..3, всё выше это уровень 4
HEAT_LEVEL_LIMITS = (1, 4, 8)

# Поля и отступы карточки проекта в пикселях
CARD_PADDING = 20
CARD_TITLE_Y = 32
CARD_DESCRIPTION_Y = 58
CARD_LINE_HEIGHT = 18
CARD_FOOTER_OFFSET = 12

# Размер блока статистики: ширина равна ширине баннера, высота вмещает числа, полосу языков и 7 рядов графика
STATS_WIDTH = 880
STATS_HEIGHT = 330

# Раскладка блока статистики: левое поле, шаг колонок чисел, базовые линии чисел и подписей
STATS_PADDING = 56
METRIC_STEP = 280
METRIC_VALUE_Y = 62
METRIC_LABEL_Y = 84

# Полоса языков, её легенда и верх графика активности
BAR_Y = 116
BAR_HEIGHT = 10
LEGEND_Y = 150
LEGEND_STEP = 160
HEAT_TOP = 184


# region Helpers
def wrap_description(text: str) -> list[str]:
    """Разбивает описание на строки карточки

    Args:
        text: Описание проекта

    Returns:
        Не больше `DESCRIPTION_LINES` строк, последняя с многоточием, если текст длиннее
    """
    lines = textwrap.wrap(text, DESCRIPTION_LINE_CHARS)

    if len(lines) <= DESCRIPTION_LINES:
        return lines

    kept = lines[:DESCRIPTION_LINES]
    kept[-1] = kept[-1][:DESCRIPTION_LINE_CHARS - 1].rstrip() + "…"

    return kept


def heat_level(count: int) -> int:
    """Переводит число вкладов за день в уровень 0..4

    Args:
        count: Число вкладов

    Returns:
        Уровень насыщенности клетки
    """
    if count <= 0:
        return 0

    for level, limit in enumerate(HEAT_LEVEL_LIMITS, start=1):
        if count <= limit:
            return level

    return len(HEAT_LEVEL_LIMITS) + 1
# endregion Helpers


# region Rendering
def render_banner(theme: Theme) -> str:
    """Рисует баннер с именем и паром над гайванем

    Args:
        theme: Тема оформления

    Returns:
        Текст SVG
    """
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 220" width="880" height="220" role="img" aria-labelledby="t d">
  <title id="t">Aeternus</title>
  <desc id="d">Backend developer, C# and .NET. Telegram Mini Apps, APIs, gongfu tea.</desc>
  <style>
    .name{{font:700 56px {MONO_FONT};fill:{theme.foreground}}}
    .role{{font:500 20px {MONO_FONT};fill:{theme.accent}}}
    .meta{{font:400 16px {SANS_FONT};fill:{theme.muted}}}
    .steam{{fill:none;stroke:{theme.accent};stroke-width:3;stroke-linecap:round;opacity:0;animation:rise 4s ease-in-out infinite}}
    .s2{{animation-delay:1.3s}}.s3{{animation-delay:2.6s}}
    @keyframes rise{{0%{{opacity:0;transform:translateY(8px)}}30%{{opacity:.8}}100%{{opacity:0;transform:translateY(-14px)}}}}
    @media (prefers-reduced-motion:reduce){{.steam{{animation:none;opacity:.5}}}}
  </style>
  <rect x=".75" y=".75" width="878.5" height="218.5" rx="16" fill="{theme.card}" stroke="{theme.border}" stroke-width="1.5"/>
  <text x="56" y="108" class="name">Aeternus</text>
  <text x="58" y="146" class="role">Backend developer · C# / .NET</text>
  <text x="58" y="180" class="meta">Telegram Mini Apps, APIs, gongfu tea. Novi Sad, Serbia.</text>
  <g transform="translate(700 70)">
    <path class="steam" d="M30 30 q-8 -12 0 -24 q8 -12 0 -24"/>
    <path class="steam s2" d="M60 30 q-8 -12 0 -24 q8 -12 0 -24"/>
    <path class="steam s3" d="M90 30 q-8 -12 0 -24 q8 -12 0 -24"/>
    <path d="M10 50 h100 q0 52 -50 52 q-50 0 -50 -52 z" fill="{theme.background}" stroke="{theme.accent}" stroke-width="3" stroke-linejoin="round"/>
    <path d="M0 50 h120" stroke="{theme.accent}" stroke-width="3" stroke-linecap="round"/>
    <path d="M35 112 h50" stroke="{theme.muted}" stroke-width="3" stroke-linecap="round"/>
  </g>
</svg>
"""


def render_card(project: Project, theme: Theme) -> str:
    """Рисует карточку проекта

    Args:
        project: Проект
        theme: Тема оформления

    Returns:
        Текст SVG
    """
    lines = "".join(f'<text x="{CARD_PADDING}" y="{CARD_DESCRIPTION_Y + index * CARD_LINE_HEIGHT}" class="desc">{escape(line)}</text>'
                    for index, line in enumerate(wrap_description(project.description)))
    footer_y = CARD_HEIGHT - CARD_FOOTER_OFFSET
    label = escape(f"{project.repo}: {project.description}", {'"': "&quot;"})

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}" width="{CARD_WIDTH}" height="{CARD_HEIGHT}"
     role="img" aria-label="{label}">
  <style>
    .title{{font:500 16px {MONO_FONT};fill:{theme.accent}}}
    .desc{{font:400 13px {SANS_FONT};fill:{theme.muted}}}
    .foot{{font:400 12px {SANS_FONT};fill:{theme.foreground}}}
  </style>
  <rect x=".5" y=".5" width="{CARD_WIDTH - 1}" height="{CARD_HEIGHT - 1}" rx="10" fill="{theme.card}" stroke="{theme.border}"/>
  <text x="{CARD_PADDING}" y="{CARD_TITLE_Y}" class="title">{escape(project.repo)}</text>
  {lines}
  <circle cx="{CARD_PADDING + 6}" cy="{footer_y - 4}" r="5" fill="{theme.accent}"/>
  <text x="{CARD_PADDING + 18}" y="{footer_y}" class="foot">{escape(project.language or "Docs")}</text>
  <text x="{CARD_WIDTH - CARD_PADDING}" y="{footer_y}" class="foot" text-anchor="end">★ {project.stars}</text>
</svg>
"""


def render_stats(stats: ProfileStats, theme: Theme) -> str:
    """Рисует блок статистики: числа, языки, график активности

    Args:
        stats: Статистика профиля
        theme: Тема оформления

    Returns:
        Текст SVG
    """
    metrics = "".join(f'<text x="{STATS_PADDING + index * METRIC_STEP}" y="{METRIC_VALUE_Y}" class="num">{value}</text>'
                      f'<text x="{STATS_PADDING + index * METRIC_STEP}" y="{METRIC_LABEL_Y}" class="lab">{label}</text>'
                      for index, (value, label) in enumerate([(stats.stars, "stars earned"),
                                                              (stats.commits, "commits in the last year"),
                                                              (stats.pull_requests, "pull requests")]))
    bar_width = STATS_WIDTH - 2 * STATS_PADDING
    bar = ""
    legend = ""
    offset = 0.0

    for index, (language, percent) in enumerate(stats.languages):
        color = theme.language_colors[index % len(theme.language_colors)]
        width = bar_width * percent / 100
        legend_x = STATS_PADDING + index * LEGEND_STEP
        bar += f'<rect x="{STATS_PADDING + offset:.1f}" y="{BAR_Y}" width="{width:.1f}" height="{BAR_HEIGHT}" fill="{color}"/>'
        legend += (f'<circle cx="{legend_x + 6}" cy="{LEGEND_Y}" r="5" fill="{color}"/>'
                   f'<text x="{legend_x + 18}" y="{LEGEND_Y + 4}" class="lab">{escape(language)} {percent:.0f}%</text>')
        offset += width

    cells = ""

    for column, week in enumerate(stats.weeks):
        for row, count in enumerate(week):
            level = heat_level(count)
            cells += (f'<rect x="{STATS_PADDING + column * (HEAT_CELL + HEAT_GAP)}" y="{HEAT_TOP + row * (HEAT_CELL + HEAT_GAP)}" '
                      f'width="{HEAT_CELL}" height="{HEAT_CELL}" rx="3" fill="{theme.accent if level else theme.border}" '
                      f'fill-opacity="{HEAT_ALPHAS[level]}"/>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {STATS_WIDTH} {STATS_HEIGHT}" width="{STATS_WIDTH}" height="{STATS_HEIGHT}"
     role="img" aria-label="GitHub statistics">
  <style>
    .num{{font:700 36px {MONO_FONT};fill:{theme.accent}}}
    .lab{{font:400 13px {SANS_FONT};fill:{theme.muted}}}
  </style>
  <rect x=".75" y=".75" width="{STATS_WIDTH - 1.5}" height="{STATS_HEIGHT - 1.5}" rx="16"
        fill="{theme.card}" stroke="{theme.border}" stroke-width="1.5"/>
  {metrics}
  <clipPath id="bar"><rect x="{STATS_PADDING}" y="{BAR_Y}" width="{bar_width}" height="{BAR_HEIGHT}" rx="5"/></clipPath>
  <g clip-path="url(#bar)">{bar}</g>
  {legend}
  {cells}
</svg>
"""
# endregion Rendering
