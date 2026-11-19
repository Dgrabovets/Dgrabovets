"""Тесты отрисовки SVG"""

import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from profilegen.profile_stats import ProfileStats
from profilegen.project import Project
from profilegen.svg_render import (DESCRIPTION_LINES, heat_level, render_banner, render_card, render_stats,
                                   wrap_description)
from profilegen.theme import THEMES


class SvgRenderTests(unittest.TestCase):
    """Проверяет обёртку описания, уровни графика и корректность XML"""

    def test_long_description_is_cut_with_ellipsis(self) -> None:
        """Длинное описание умещается в три строки и заканчивается многоточием"""
        lines = wrap_description("word " * 60)

        self.assertEqual(len(lines), DESCRIPTION_LINES)
        self.assertTrue(lines[-1].endswith("…"))

    def test_heat_levels(self) -> None:
        """Границы уровней графика: 0 пусто, 1 до 1, 2 до 4, 3 до 8, дальше 4"""
        self.assertEqual([heat_level(count) for count in (0, 1, 2, 4, 5, 8, 9)], [0, 1, 2, 2, 3, 3, 4])

    def test_all_svg_are_valid_xml_and_escape_text(self) -> None:
        """Спецсимволы в описании не ломают XML, все три SVG разбираются парсером"""
        project = Project(repo="A&B", section="current", description='Tea <diary> "for" friends', language="C#", stars=1)
        stats = ProfileStats(stars=1, commits=2, pull_requests=3, languages=[("C#", 60.0), ("Python", 40.0)],
                             weeks=[[0, 1, 5, 9, 0, 0, 2]])

        for theme in THEMES:
            for text in (render_banner(theme), render_card(project, theme), render_stats(stats, theme)):
                ElementTree.fromstring(text)


if __name__ == "__main__":
    unittest.main()
