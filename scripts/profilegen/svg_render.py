"""Отрисовка SVG: баннер, заголовки разделов, значки стека, карточки проектов и статистика"""

import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from .card_motion import render_motion
from .font_enum import FontEnum
from .glyph_text import printable, text_path, text_width
from .profile_stats import ProfileStats
from .project import Project
from .project_kind_enum import ProjectKindEnum
from .theme import Theme

# Готовые шапки бренда с текстом в контурах и анимированной петлёй, копии `assets/header-<тема>.svg` из папки темы бренда
BANNER_DIR = Path(__file__).parent

# Скругления рамок: заголовки и значки, карточки и плитки, блок статистики как у шапки
SMALL_RADIUS = 8
CARD_RADIUS = 12
BLOCK_RADIUS = 16

# Толщина рамки: половина уходит внутрь отступа, чтобы линия не обрезалась краем
BORDER_WIDTH = 1.5

# Размер карточки проекта
CARD_WIDTH = 340
CARD_HEIGHT = 148

# Сколько символов описания помещается в строку карточки при `CARD_DESCRIPTION_SIZE`
DESCRIPTION_LINE_CHARS = 39

# Сколько строк описания показывается, остальное заменяется многоточием
DESCRIPTION_LINES = 3

# Подписи под числами статистики
COMMITS_CAPTION = "commits in the last year"
PULL_REQUESTS_CAPTION = "pull requests in the last year"

# Размер клетки графика активности и зазор между клетками
HEAT_CELL = 16
HEAT_GAP = 3
HEAT_RADIUS = 3

# Сторона квадрата на уровнях 0..4: активность видна по размеру и без различения цветов, пустой день это точка
HEAT_SIDES = (5, 8, 11, 14, 16)

# Подсказка «Less … More» под графиком: подписи, отступ от нижнего края, шаг квадратов, зазор до подписей и базовая линия текста
SCALE_LESS = "Less"
SCALE_MORE = "More"
SCALE_RISE = 26
SCALE_STEP = 20
SCALE_GAP = 8
SCALE_TEXT_Y = 13

# Верхние границы числа вкладов за день для уровней 1..3, всё выше это уровень 4
HEAT_LEVEL_LIMITS = (1, 4, 8)

# Поля и базовые линии карточки проекта в пикселях
CARD_PADDING = 20
# Название стоит правее квадратной метки
CARD_TITLE_X = 36
CARD_TITLE_Y = 34
CARD_DESCRIPTION_Y = 62
CARD_LINE_HEIGHT = 19
CARD_LABEL_Y = 132

# Размеры шрифтов карточки: название, описание, подпись языка
CARD_TITLE_SIZE = 17
CARD_DESCRIPTION_SIZE = 14.5
CARD_LABEL_SIZE = 13

# Квадратная метка перед названием проекта
CARD_MARK_X = 20
CARD_MARK_Y = 24
CARD_MARK_SIZE = 8

# Плитка легенды анимаций: размер, поле, базовые линии названия вида и анимации, их размеры
LEGEND_WIDTH = 207
LEGEND_HEIGHT = 56
LEGEND_PADDING = 14
LEGEND_TITLE_Y = 24
LEGEND_NAME_Y = 43
LEGEND_TITLE_SIZE = 14
LEGEND_NAME_SIZE = 12
# Где в плитке инструмента мигает курсор: правый край условной подписи и её базовая линия
LEGEND_CURSOR = (LEGEND_WIDTH - 36, 36)
# Сдвиг начала анимации в плитке по виду проекта: на снимке без движения видны блик и рамка
LEGEND_DELAYS = {ProjectKindEnum.BACKEND: 0.4, ProjectKindEnum.APP: 1.0, ProjectKindEnum.TOOL: 0.0, ProjectKindEnum.EARLY: 2.0}

# Заголовок раздела: высота, поле, зазор после акцентной черты и разрядка букв как у подписи в шапке
HEADING_HEIGHT = 34
HEADING_PADDING = 14
HEADING_GAP = 12
HEADING_SPACING = 4
HEADING_FONT_SIZE = 14
HEADING_TEXT_Y = 22

# Акцентная черта из шапки бренда и скругление акцентных черт
ACCENT_BAR_WIDTH = 28
ACCENT_BAR_HEIGHT = 4
ACCENT_RADIUS = 2

# Значок стека: высота, левое поле под вертикальную черту, правое поле и размер шрифта
BADGE_HEIGHT = 28
BADGE_TEXT_X = 22
BADGE_PADDING = 12
BADGE_FONT_SIZE = 13
BADGE_TEXT_Y = 18

# Вертикальная акцентная черта значка
BADGE_MARK_X = 10
BADGE_MARK_Y = 8
BADGE_MARK_WIDTH = 4
BADGE_MARK_HEIGHT = 12

# Размер блока статистики: ширина равна ширине баннера, высота вмещает плитки, полосу языков, 7 рядов графика и подсказку под ним
STATS_WIDTH = 880
STATS_HEIGHT = 376

# Раскладка статистики: боковое поле центрирует график из 40 недель, затем плитки с числами
STATS_PADDING = 62
TILE_Y = 24
TILE_HEIGHT = 88
TILE_GAP = 16

# Внутри плитки: левое поле, базовые линии и размеры числа и подписи
TILE_PADDING = 20
TILE_VALUE_Y = 46
TILE_CAPTION_Y = 70
TILE_VALUE_SIZE = 34
STATS_FONT_SIZE = 13

# Полоса языков, её легенда и верх графика активности
BAR_Y = 134
BAR_HEIGHT = 10
LEGEND_Y = 168
LEGEND_GAP = 28
LEGEND_DOT_RADIUS = 5
LEGEND_TEXT_X = 17
LEGEND_DOT_RISE = 4
HEAT_TOP = 190


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


def _share(percent: float) -> str:
    """Пишет долю языка целым числом

    Args:
        percent: Доля в процентах

    Returns:
        Процент, а для долей меньше одного `<1%`, чтобы язык не выглядел отсутствующим
    """
    return f"{percent:.0f}%" if percent >= 1 else "<1%"


def _svg(width: float,
         height: int,
         label: str,
         body: str) -> str:
    """Оборачивает содержимое в SVG с подписью для экранных дикторов

    Args:
        width: Ширина
        height: Высота
        label: Текст картинки
        body: Внутренние элементы

    Returns:
        Текст SVG
    """
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height}" width="{width:g}" height="{height}" '
            f'role="img" aria-label="{escape(label, {chr(34): "&quot;"})}">\n{body}\n</svg>\n')


def _box(x: float,
         y: float,
         width: float,
         height: int,
         radius: int,
         fill: str,
         border: str) -> str:
    """Рисует прямоугольник с тонкой рамкой целиком внутри заданных границ

    Args:
        x: Левый край
        y: Верхний край
        width: Ширина
        height: Высота
        radius: Скругление
        fill: Заливка
        border: Цвет рамки

    Returns:
        Элемент `rect`
    """
    inset = BORDER_WIDTH / 2

    return (f'<rect x="{x + inset:g}" y="{y + inset:g}" width="{width - BORDER_WIDTH:g}" height="{height - BORDER_WIDTH:g}" '
            f'rx="{radius}" fill="{fill}" stroke="{border}" stroke-width="{BORDER_WIDTH:g}"/>')

def _language_caption(language: str, percent: float) -> str:
    """Собирает подпись языка для легенды и описания

    Args:
        language: Название языка из GitHub
        percent: Доля в процентах

    Returns:
        Название и доля
    """
    return f"{printable(language, FontEnum.SANS_MEDIUM)} {_share(percent)}"


def _heat_cell(x: float,
               y: int,
               level: int,
               theme: Theme) -> str:
    """Рисует квадрат активности по центру клетки

    Args:
        x: Левый край клетки
        y: Верхний край клетки
        level: Уровень 0..4
        theme: Тема оформления

    Returns:
        Элемент `rect`
    """
    side = HEAT_SIDES[level]
    inset = (HEAT_CELL - side) / 2

    return (f'<rect x="{x + inset:g}" y="{y + inset:g}" width="{side}" height="{side}" rx="{min(HEAT_RADIUS, side // 3)}" '
            f'fill="{theme.heat_colors[level]}"/>')


def _heat_scale(theme: Theme) -> str:
    """Рисует подсказку «меньше или больше», прижатую к правому краю графика

    Args:
        theme: Тема оформления

    Returns:
        Элементы SVG
    """
    top = STATS_HEIGHT - SCALE_RISE
    more_x = round(STATS_WIDTH - STATS_PADDING - text_width(SCALE_MORE, FontEnum.SANS_MEDIUM, STATS_FONT_SIZE), 1)
    cells_x = round(more_x - SCALE_GAP - (len(HEAT_SIDES) - 1) * SCALE_STEP - HEAT_CELL, 1)
    less_x = round(cells_x - SCALE_GAP - text_width(SCALE_LESS, FontEnum.SANS_MEDIUM, STATS_FONT_SIZE), 1)

    return (text_path(SCALE_LESS, less_x, top + SCALE_TEXT_Y, FontEnum.SANS_MEDIUM, STATS_FONT_SIZE, theme.muted)
            + "".join(_heat_cell(cells_x + level * SCALE_STEP, top, level, theme) for level in range(len(HEAT_SIDES)))
            + text_path(SCALE_MORE, more_x, top + SCALE_TEXT_Y, FontEnum.SANS_MEDIUM, STATS_FONT_SIZE, theme.muted))
# endregion Helpers


# region Rendering
def render_banner(theme: Theme) -> str:
    """Читает шапку бренда нужной темы

    Args:
        theme: Тема оформления

    Returns:
        Текст SVG
    """
    return (BANNER_DIR / f"header-{theme.name}.svg").read_text(encoding="utf-8")


def render_heading(title: str, theme: Theme) -> str:
    """Рисует заголовок раздела: акцентная черта и заглавные буквы вразрядку

    Args:
        title: Название раздела
        theme: Тема оформления

    Returns:
        Текст SVG
    """
    caps = title.upper()
    text_x = HEADING_PADDING + ACCENT_BAR_WIDTH + HEADING_GAP
    width = round(text_x + text_width(caps, FontEnum.MONO_MEDIUM, HEADING_FONT_SIZE, HEADING_SPACING) + HEADING_PADDING)

    return _svg(width, HEADING_HEIGHT, title,
                _box(0, 0, width, HEADING_HEIGHT, SMALL_RADIUS, theme.background, theme.border)
                + f'<rect x="{HEADING_PADDING}" y="{(HEADING_HEIGHT - ACCENT_BAR_HEIGHT) // 2}" width="{ACCENT_BAR_WIDTH}" '
                  f'height="{ACCENT_BAR_HEIGHT}" rx="{ACCENT_RADIUS}" fill="{theme.accent}"/>'
                + text_path(caps, text_x, HEADING_TEXT_Y, FontEnum.MONO_MEDIUM, HEADING_FONT_SIZE, theme.label, HEADING_SPACING))


def render_badge(label: str, theme: Theme) -> str:
    """Рисует значок технологии

    Args:
        label: Название технологии
        theme: Тема оформления

    Returns:
        Текст SVG
    """
    width = round(BADGE_TEXT_X + text_width(label, FontEnum.MONO_MEDIUM, BADGE_FONT_SIZE) + BADGE_PADDING)

    return _svg(width, BADGE_HEIGHT, label,
                _box(0, 0, width, BADGE_HEIGHT, SMALL_RADIUS, theme.card, theme.border)
                + f'<rect x="{BADGE_MARK_X}" y="{BADGE_MARK_Y}" width="{BADGE_MARK_WIDTH}" height="{BADGE_MARK_HEIGHT}" '
                  f'rx="{ACCENT_RADIUS}" fill="{theme.accent}"/>'
                + text_path(label, BADGE_TEXT_X, BADGE_TEXT_Y, FontEnum.MONO_MEDIUM, BADGE_FONT_SIZE, theme.foreground))


def render_card(project: Project,
                theme: Theme,
                delay: float = 0.0) -> str:
    """Рисует карточку проекта с анимацией его вида

    Args:
        project: Проект
        theme: Тема оформления
        delay: Сдвиг начала анимации в секундах

    Returns:
        Текст SVG
    """
    lines = "".join(text_path(line, CARD_PADDING, CARD_DESCRIPTION_Y + index * CARD_LINE_HEIGHT,
                              FontEnum.SANS_MEDIUM, CARD_DESCRIPTION_SIZE, theme.muted)
                    for index, line in enumerate(wrap_description(project.description)))
    label = printable(project.label, FontEnum.MONO_MEDIUM)
    footer = (text_path(label, CARD_PADDING, CARD_LABEL_Y, FontEnum.MONO_MEDIUM, CARD_LABEL_SIZE, theme.label)
              if label
              else "")

    # Анимация идёт сразу после фона: длинные строки доходят до правого края, и текст должен лежать сверху
    motion = render_motion(project.kind, theme, delay, (CARD_WIDTH, CARD_HEIGHT, CARD_RADIUS),
                           (CARD_PADDING + text_width(label, FontEnum.MONO_MEDIUM, CARD_LABEL_SIZE), CARD_LABEL_Y))

    return _svg(CARD_WIDTH, CARD_HEIGHT, f"{project.repo}: {project.description}",
                _box(0, 0, CARD_WIDTH, CARD_HEIGHT, CARD_RADIUS, theme.card, theme.border)
                + motion
                + f'<rect x="{CARD_MARK_X}" y="{CARD_MARK_Y}" width="{CARD_MARK_SIZE}" height="{CARD_MARK_SIZE}" rx="{ACCENT_RADIUS}" '
                  f'fill="{theme.accent}"/>'
                + text_path(project.repo, CARD_TITLE_X, CARD_TITLE_Y, FontEnum.MONO_BOLD, CARD_TITLE_SIZE, theme.foreground)
                + lines
                + footer)


def render_legend(kind: ProjectKindEnum,
                  title: str,
                  name: str,
                  theme: Theme) -> str:
    """Рисует плитку легенды с живой анимацией своего вида проекта

    Args:
        kind: Вид проекта
        title: Название вида
        name: Название анимации
        theme: Тема оформления

    Returns:
        Текст SVG
    """
    motion = render_motion(kind, theme, LEGEND_DELAYS[kind], (LEGEND_WIDTH, LEGEND_HEIGHT, SMALL_RADIUS), LEGEND_CURSOR)

    return _svg(LEGEND_WIDTH, LEGEND_HEIGHT, f"{title}: {name}",
                _box(0, 0, LEGEND_WIDTH, LEGEND_HEIGHT, SMALL_RADIUS, theme.card, theme.border)
                + motion
                + text_path(title, LEGEND_PADDING, LEGEND_TITLE_Y, FontEnum.MONO_BOLD, LEGEND_TITLE_SIZE, theme.foreground)
                + text_path(name, LEGEND_PADDING, LEGEND_NAME_Y, FontEnum.MONO_MEDIUM, LEGEND_NAME_SIZE, theme.label))


def render_stats(stats: ProfileStats, theme: Theme) -> str:
    """Рисует блок статистики: плитки с числами, языки, график активности

    Args:
        stats: Статистика профиля
        theme: Тема оформления

    Returns:
        Текст SVG
    """
    metrics = [(stats.commits, COMMITS_CAPTION), (stats.pull_requests, PULL_REQUESTS_CAPTION)]
    content_width = STATS_WIDTH - 2 * STATS_PADDING
    tile_width = (content_width - TILE_GAP * (len(metrics) - 1)) / len(metrics)
    tiles = ""

    for index, (value, caption) in enumerate(metrics):
        x = STATS_PADDING + index * (tile_width + TILE_GAP)
        tiles += (_box(x, TILE_Y, tile_width, TILE_HEIGHT, CARD_RADIUS, theme.card, theme.border)
                  + text_path(str(value), x + TILE_PADDING, TILE_Y + TILE_VALUE_Y, FontEnum.MONO_BOLD, TILE_VALUE_SIZE, theme.label)
                  + text_path(caption, x + TILE_PADDING, TILE_Y + TILE_CAPTION_Y, FontEnum.SANS_MEDIUM, STATS_FONT_SIZE, theme.muted))

    bar = ""
    legend = ""
    offset = 0.0
    legend_x = float(STATS_PADDING)

    for index, (language, percent) in enumerate(stats.languages):
        color = theme.language_colors[index % len(theme.language_colors)]
        width = content_width * percent / 100
        caption = _language_caption(language, percent)

        bar += f'<rect x="{STATS_PADDING + offset:.1f}" y="{BAR_Y}" width="{width:.1f}" height="{BAR_HEIGHT}" fill="{color}"/>'
        legend += (f'<circle cx="{legend_x + LEGEND_DOT_RADIUS:.1f}" cy="{LEGEND_Y - LEGEND_DOT_RISE}" r="{LEGEND_DOT_RADIUS}" fill="{color}"/>'
                   + text_path(caption, round(legend_x + LEGEND_TEXT_X, 1), LEGEND_Y, FontEnum.SANS_MEDIUM, STATS_FONT_SIZE, theme.muted))

        offset += width
        legend_x += LEGEND_TEXT_X + text_width(caption, FontEnum.SANS_MEDIUM, STATS_FONT_SIZE) + LEGEND_GAP

    cells = "".join(_heat_cell(STATS_PADDING + column * (HEAT_CELL + HEAT_GAP), HEAT_TOP + row * (HEAT_CELL + HEAT_GAP), heat_level(count), theme)
                    for column, week in enumerate(stats.weeks)
                    for row, count in enumerate(week))

    # Числа и языки повторены в подписи: контуры букв экранный диктор не прочитает
    description = ", ".join([f"{value} {caption}" for value, caption in metrics]
                            + [_language_caption(language, percent) for language, percent in stats.languages])

    return _svg(STATS_WIDTH, STATS_HEIGHT, f"GitHub statistics: {description}",
                _box(0, 0, STATS_WIDTH, STATS_HEIGHT, BLOCK_RADIUS, theme.background, theme.border)
                + tiles
                + f'<clipPath id="bar"><rect x="{STATS_PADDING}" y="{BAR_Y}" width="{content_width}" height="{BAR_HEIGHT}" '
                  f'rx="{BAR_HEIGHT // 2}"/></clipPath>'
                  f'<g clip-path="url(#bar)">{bar}</g>'
                + legend
                + cells
                + _heat_scale(theme))
# endregion Rendering
