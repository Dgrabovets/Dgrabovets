"""Тесты отрисовки SVG"""

import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_profile import LEGEND
from profilegen.font_enum import FontEnum
from profilegen.glyph_text import text_path, text_width
from profilegen.profile_stats import ProfileStats
from profilegen.project import Project
from profilegen.project_kind_enum import ProjectKindEnum
from profilegen.svg_render import (CARD_DESCRIPTION_SIZE, CARD_PADDING, CARD_TITLE_SIZE, CARD_TITLE_X, CARD_WIDTH, DESCRIPTION_LINES,
                                   HEAT_SIDES, LEGEND_NAME_SIZE, LEGEND_PADDING, LEGEND_WIDTH, heat_level, render_badge, render_banner,
                                   render_card, render_heading, render_legend, render_stats, wrap_description)
from profilegen.theme import DARK, LIGHT, THEMES

# Список проектов профиля, по нему проверяется, что тексты помещаются в карточки
PROJECTS_PATH = Path(__file__).resolve().parents[1] / "projects.json"


class SvgRenderTests(unittest.TestCase):
    """Проверяет обёртку описания, уровни графика, контуры текста и корректность XML"""

    def test_long_description_is_cut_with_ellipsis(self) -> None:
        """Длинное описание умещается в три строки и заканчивается многоточием"""
        lines = wrap_description("word " * 60)

        self.assertEqual(len(lines), DESCRIPTION_LINES)
        self.assertTrue(lines[-1].endswith("…"))

    def test_real_descriptions_fit_cards(self) -> None:
        """Описания из projects.json не обрезаются и не выходят за поля карточки"""
        for entry in json.loads(PROJECTS_PATH.read_text(encoding="utf-8")):
            for line in wrap_description(entry["description"]):
                self.assertFalse(line.endswith("…"), entry["repo"])
                self.assertLessEqual(text_width(line, FontEnum.SANS_MEDIUM, CARD_DESCRIPTION_SIZE), CARD_WIDTH - 2 * CARD_PADDING, line)

    def test_heat_levels(self) -> None:
        """Границы уровней графика: 0 пусто, 1 до 1, 2 до 4, 3 до 8, дальше 4"""
        self.assertEqual([heat_level(count) for count in (0, 1, 2, 4, 5, 8, 9)], [0, 1, 2, 2, 3, 3, 4])

    def test_activity_levels_differ_in_size_and_color(self) -> None:
        """Пустой день и четыре уровня активности различаются и размером, и цветом"""
        stats = ProfileStats(commits=0, pull_requests=0, languages=[], weeks=[[0, 1, 4, 8, 9]])

        for theme in THEMES:
            svg = render_stats(stats, theme)

            self.assertEqual(sorted(set(HEAT_SIDES)), list(HEAT_SIDES))
            self.assertEqual(len(set(theme.heat_colors)), len(HEAT_SIDES))

            for side, color in zip(HEAT_SIDES, theme.heat_colors):
                self.assertRegex(svg, rf'width="{side}" height="{side}" rx="\d+" fill="{color}"')

    def test_tiny_language_share_is_not_zero(self) -> None:
        """Доля 0.3 процента пишется как меньше одного, а не как ноль"""
        stats = ProfileStats(commits=0, pull_requests=0, languages=[("CSS", 0.3)], weeks=[])

        self.assertIn("0 pull requests in the last year, CSS &lt;1%", render_stats(stats, DARK))

    def test_unknown_symbol_is_reported(self) -> None:
        """Символ вне таблицы контуров роняет сборку, а не пропадает молча"""
        with self.assertRaises(ValueError):
            text_path("Ж", 0, 0, FontEnum.SANS_MEDIUM, 13, "#fff")

    def test_all_svg_are_valid_xml_and_escape_text(self) -> None:
        """Спецсимволы в описании не ломают XML, все SVG разбираются парсером и не содержат живого текста"""
        project = Project(repo="A&B", section="current", description='Tea <diary> "for" friends', label="C#")
        stats = ProfileStats(commits=2, pull_requests=3, languages=[("C#", 60.0), ("Python", 40.0)],
                             weeks=[[0, 1, 5, 9, 0, 0, 2]])

        for theme in THEMES:
            for text in (render_banner(theme), render_heading("Current", theme), render_badge("C#", theme),
                         render_card(project, theme), render_stats(stats, theme)):
                ElementTree.fromstring(text)
                # GitHub не подгружает веб-шрифты, поэтому весь текст должен быть контурами
                self.assertNotIn("<text", text)

    def test_loop_animation_only_in_banner(self) -> None:
        """Петля бесконечности есть в шапке и нигде больше"""
        project = Project(repo="A", section="current", description="B", label="")
        stats = ProfileStats(commits=0, pull_requests=0, languages=[], weeks=[])

        for theme in THEMES:
            self.assertIn('class="flow"', render_banner(theme))

        for text in (render_heading("Current", DARK), render_badge("C#", DARK), render_card(project, DARK), render_stats(stats, DARK)):
            self.assertNotIn("flow", text)

    def test_each_project_kind_has_its_own_animation(self) -> None:
        """У каждого вида своя анимация под текстом, она отключается настройкой движения и разбирается парсером"""
        classes = ('class="column"', 'class="glare"', 'class="cursor"', 'class="breath"')

        for theme in THEMES:
            cards = [render_card(Project(repo="A", section="current", description="B", label="C#", kind=kind), theme, 1.7)
                     for kind in (ProjectKindEnum.BACKEND, ProjectKindEnum.APP, ProjectKindEnum.TOOL, ProjectKindEnum.EARLY)]

            for expected, card in zip(classes, cards):
                ElementTree.fromstring(card)
                self.assertEqual([name for name in classes if name in card], [expected])
                self.assertIn("prefers-reduced-motion", card)
                self.assertLess(card.index(expected), card.index("<g transform"))

    def test_names_fit_cards(self) -> None:
        """Название из projects.json после метки не выходит за правое поле карточки"""
        for entry in json.loads(PROJECTS_PATH.read_text(encoding="utf-8")):
            self.assertLessEqual(CARD_TITLE_X + text_width(entry["repo"], FontEnum.MONO_BOLD, CARD_TITLE_SIZE), CARD_WIDTH - 4, entry["repo"])

    def test_legend_shows_the_animation_of_its_kind(self) -> None:
        """Плитка легенды двигается так же, как карточки этого вида, и помещает подписи"""
        classes = ('class="column"', 'class="glare"', 'class="cursor"', 'class="breath"')

        for theme in THEMES:
            for entry, expected in zip(LEGEND, classes):
                tile = render_legend(entry.kind, entry.title, entry.name, theme)

                ElementTree.fromstring(tile)
                self.assertEqual([name for name in classes if name in tile], [expected])
                self.assertLessEqual(LEGEND_PADDING + text_width(entry.name, FontEnum.MONO_MEDIUM, LEGEND_NAME_SIZE), LEGEND_WIDTH - 40)

    def test_light_files_use_light_colors(self) -> None:
        """Светлые картинки рисуются своей палитрой: фон шапки и значка не остаётся тёмным"""
        self.assertIn(f'fill="{LIGHT.background}"', render_banner(LIGHT))
        self.assertIn(f'fill="{LIGHT.card}"', render_badge("C#", LIGHT))
        self.assertNotIn(DARK.card, render_badge("C#", LIGHT))


if __name__ == "__main__":
    unittest.main()
