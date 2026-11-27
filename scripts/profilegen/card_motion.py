"""Анимации карточек проектов: у каждого вида проекта своя, рисуются под текстом"""

from .project_kind_enum import ProjectKindEnum
from .theme import Theme

# Анимация выключается, если в системе просят меньше движения: без неё блик и рамка не видны, колонки и курсор стоят
STILL = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"

# Колонки света у правого края (сервисы): отступ первой от правого края, шаг, число, длительность и задержка между соседними.
# Отступ такой, чтобы колонки стояли правее самой длинной строки описания и не шли под текстом
COLUMN_RIGHT_GAP = 31
# Высота, под которую заданы колонки: в более низкой плитке они сжимаются по вертикали
COLUMN_DESIGN_HEIGHT = 148
COLUMN_STEP = 3.8
COLUMN_COUNT = 8
COLUMN_SECONDS = 5
COLUMN_LAG = 0.45
# Каждая четвёртая колонка широкая, остальные тонкие
COLUMN_WIDE = 3
COLUMN_THIN = 1.6
COLUMN_WIDE_EVERY = 4
# Верх и высота колонки разбросаны остатком от деления: рисунок неровный, но одинаковый при каждой сборке
COLUMN_TOP = 14
COLUMN_TOP_STEP = 37
COLUMN_TOP_SPREAD = 52
COLUMN_HEIGHT = 46
COLUMN_HEIGHT_STEP = 23
COLUMN_HEIGHT_SPREAD = 48

# Косой блик (приложения с интерфейсом): ширина полосы, наклон в градусах, путь слева направо, сила и длительность
GLARE_WIDTH = 90
GLARE_SKEW = -18
GLARE_FROM = -140
GLARE_TO = 460
GLARE_OPACITY = 0.2
GLARE_SECONDS = 6

# Загорающаяся рамка (проекты на ранней стадии)
BREATH_WIDTH = 2
BREATH_SECONDS = 5
# Отступ рамки и блика от края карточки, чтобы линия не обрезалась
EDGE = 1

# Мигающий курсор терминала (инструменты) после подписи языка
CURSOR_GAP = 6
CURSOR_WIDTH = 8
CURSOR_HEIGHT = 14
# Насколько курсор поднят над базовой линией подписи
CURSOR_RISE = 11
CURSOR_SECONDS = 1.1


# region Motions
def _style(rules: str) -> str:
    """Оборачивает правила CSS в стиль с отключением движения

    Args:
        rules: Правила CSS

    Returns:
        Элемент `style`
    """
    return f"<style>{rules}{STILL}</style>"


def _columns(theme: Theme,
             delay: float,
             width: int,
             height: int) -> str:
    """Рисует колонки света, которые медленно разгораются

    Args:
        theme: Тема оформления
        delay: Сдвиг начала в секундах
        width: Ширина картинки
        height: Высота картинки

    Returns:
        Элементы SVG
    """
    bars = "".join(f'<rect class="column" x="{width - COLUMN_RIGHT_GAP + index * COLUMN_STEP:g}" '
                   f'y="{COLUMN_TOP + index * COLUMN_TOP_STEP % COLUMN_TOP_SPREAD}" '
                   f'width="{COLUMN_THIN if index % COLUMN_WIDE_EVERY else COLUMN_WIDE}" '
                   f'height="{COLUMN_HEIGHT + index * COLUMN_HEIGHT_STEP % COLUMN_HEIGHT_SPREAD}" fill="url(#fade)" '
                   f'style="animation-delay:{-(delay + index * COLUMN_LAG):g}s"/>'
                   for index in range(COLUMN_COUNT))

    if height < COLUMN_DESIGN_HEIGHT:
        bars = f'<svg viewBox="0 0 {width} {COLUMN_DESIGN_HEIGHT}" width="{width}" height="{height}" preserveAspectRatio="none">{bars}</svg>'

    return (_style(f".column{{opacity:.15;animation:glow {COLUMN_SECONDS}s ease-in-out infinite}}@keyframes glow{{50%{{opacity:.8}}}}")
            + f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{theme.columns}" stop-opacity="0"/>'
              f'<stop offset=".7" stop-color="{theme.columns}"/><stop offset="1" stop-color="{theme.columns}" stop-opacity="0"/></linearGradient>'
            + bars)


def _glare(theme: Theme,
           delay: float,
           width: int,
           height: int,
           radius: int) -> str:
    """Рисует мягкий косой блик, который проходит по карточке и пропадает

    Args:
        theme: Тема оформления
        delay: Сдвиг начала в секундах
        width: Ширина карточки
        height: Высота карточки
        radius: Скругление карточки

    Returns:
        Элементы SVG
    """
    return (_style(f".glare{{transform:translateX({GLARE_FROM}px);animation:glare {GLARE_SECONDS}s ease-in-out {-delay:g}s infinite}}"
                   f"@keyframes glare{{0%{{transform:translateX({GLARE_FROM}px)}}45%,100%{{transform:translateX({GLARE_TO}px)}}}}")
            + f'<clipPath id="inside"><rect x="{EDGE}" y="{EDGE}" width="{width - 2 * EDGE}" height="{height - 2 * EDGE}" rx="{radius}"/></clipPath>'
              f'<linearGradient id="light" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{theme.accent}" stop-opacity="0"/>'
              f'<stop offset=".5" stop-color="{theme.accent}" stop-opacity="{GLARE_OPACITY}"/>'
              f'<stop offset="1" stop-color="{theme.accent}" stop-opacity="0"/></linearGradient>'
              f'<g clip-path="url(#inside)"><g class="glare"><rect width="{GLARE_WIDTH}" height="{height}" fill="url(#light)" '
              f'transform="skewX({GLARE_SKEW})"/></g></g>')


def _breath(theme: Theme,
            delay: float,
            width: int,
            height: int,
            radius: int) -> str:
    """Рисует рамку, которая медленно загорается и гаснет

    Args:
        theme: Тема оформления
        delay: Сдвиг начала в секундах
        width: Ширина карточки
        height: Высота карточки
        radius: Скругление карточки

    Returns:
        Элементы SVG
    """
    return (_style(f".breath{{opacity:0;animation:breath {BREATH_SECONDS}s ease-in-out {-delay:g}s infinite}}"
                   "@keyframes breath{50%{opacity:1}}")
            + f'<rect class="breath" x="{EDGE}" y="{EDGE}" width="{width - 2 * EDGE}" height="{height - 2 * EDGE}" rx="{radius}" fill="none" '
              f'stroke="{theme.accent}" stroke-width="{BREATH_WIDTH}"/>')


def _cursor(theme: Theme,
            delay: float,
            label_end: float,
            baseline: int) -> str:
    """Рисует мигающий курсор терминала после подписи языка

    Args:
        theme: Тема оформления
        delay: Сдвиг начала в секундах
        label_end: Правый край подписи
        baseline: Базовая линия подписи

    Returns:
        Элементы SVG
    """
    return (_style(f".cursor{{animation:blink {CURSOR_SECONDS}s steps(1) {-delay:g}s infinite}}@keyframes blink{{50%{{opacity:0}}}}")
            + f'<rect class="cursor" x="{label_end + CURSOR_GAP:.1f}" y="{baseline - CURSOR_RISE}" width="{CURSOR_WIDTH}" '
              f'height="{CURSOR_HEIGHT}" fill="{theme.accent}"/>')
# endregion Motions


def render_motion(kind: ProjectKindEnum,
                  theme: Theme,
                  delay: float,
                  size: tuple[int, int, int],
                  label_position: tuple[float, int]) -> str:
    """Выбирает анимацию по виду проекта

    Args:
        kind: Вид проекта
        theme: Тема оформления
        delay: Сдвиг начала в секундах, чтобы карточки не двигались разом
        size: Ширина, высота и скругление карточки
        label_position: Правый край и базовая линия подписи языка

    Returns:
        Элементы SVG
    """
    if kind is ProjectKindEnum.BACKEND:
        return _columns(theme, delay, *size[:2])

    if kind is ProjectKindEnum.APP:
        return _glare(theme, delay, *size)

    if kind is ProjectKindEnum.EARLY:
        return _breath(theme, delay, *size)

    return _cursor(theme, delay, *label_position)
