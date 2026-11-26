"""Тесты сборки README"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_profile import _load_projects, _picture, _section_html
from profilegen import settings
from profilegen.project import Project


class PictureTests(unittest.TestCase):
    """Проверяет тег картинки"""

    def test_both_theme_files_are_referenced(self) -> None:
        """Тёмный файл идёт в `source`, светлый остаётся запасным в `img`, без ширины атрибута нет"""
        self.assertEqual(_picture("assets/banner", "Banner"),
                         '<picture><source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">'
                         '<img src="assets/banner-light.svg" alt="Banner"></picture>')

    def test_width_is_added(self) -> None:
        """Заданная ширина попадает в `img`"""
        self.assertIn('alt="Banner" width="100%">', _picture("assets/banner", "Banner", "100%"))

    def test_alt_is_escaped(self) -> None:
        """Кавычки и угловые скобки не разрывают атрибут"""
        self.assertIn('alt="&lt;a&gt; &amp; &quot;b&quot;"', _picture("assets/banner", '<a> & "b"'))


class SectionHtmlTests(unittest.TestCase):
    """Проверяет ряд карточек секции"""

    def setUp(self) -> None:
        """Фиксирует логин, чтобы ссылки не зависели от окружения"""
        patcher = mock.patch.dict(os.environ, {"PROFILE_USER": "owner"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_cards_link_to_repositories_in_order(self) -> None:
        """Каждая карточка ведёт в свой репозиторий, порядок сохраняется, таблицы нет"""
        html = _section_html([self._project("First"), self._project("Second"), self._project("Third")])

        self.assertEqual(html.count("<a href="), 3)
        self.assertLess(html.index('href="https://github.com/owner/First"'), html.index('href="https://github.com/owner/Second"'))
        self.assertIn('srcset="assets/cards/Third-dark.svg"', html)
        self.assertNotIn("<table", html)

    def test_card_has_fixed_width_and_descriptive_alt(self) -> None:
        """Ширина карточки в пикселях, а описание читается экранным диктором"""
        html = _section_html([self._project("First")])

        self.assertIn('alt="First: About First" width="400"', html)

    def test_empty_section(self) -> None:
        """Пустая секция даёт пустой абзац"""
        self.assertEqual(_section_html([]), '<p align="center">\n\n</p>')

    @staticmethod
    def _project(repo: str) -> Project:
        """Создаёт проект для проверки

        Args:
            repo: Имя репозитория

        Returns:
            Проект
        """
        return Project(repo=repo, section="current", description=f"About {repo}", label="C#")


class LoadProjectsTests(unittest.TestCase):
    """Проверяет чтение projects.json"""

    def test_github_language_wins_and_label_fills_the_gap(self) -> None:
        """Порядок из файла, язык GitHub важнее `label`, без обоих подпись пустая"""
        entries = [self._entry("Detected", label="Unity"), self._entry("Fallback", label="Unity"), self._entry("Nothing")]
        repos = {"Nothing": {"language": None}, "Fallback": {"language": None}, "Detected": {"language": "C#"}}

        projects = self._load(entries, repos)

        self.assertEqual([(project.repo, project.label) for project in projects],
                         [("Detected", "C#"), ("Fallback", "Unity"), ("Nothing", "")])

    def test_missing_repository_fails(self) -> None:
        """Репозиторий, которого нет среди публичных, останавливает сборку"""
        with self.assertRaises(KeyError):
            self._load([self._entry("Private")], {})

    @staticmethod
    def _entry(repo: str, **extra: str) -> dict[str, str]:
        """Создаёт запись projects.json

        Args:
            repo: Имя репозитория
            extra: Необязательные поля

        Returns:
            Запись
        """
        return {"repo": repo, "section": "current", "description": "Text", **extra}

    def _load(self, entries: list[dict[str, str]], repos: dict[str, dict]) -> list[Project]:
        """Читает проекты из временного projects.json

        Args:
            entries: Записи файла
            repos: Ответ GitHub о репозиториях

        Returns:
            Прочитанные проекты
        """
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(settings, "ROOT_DIR", Path(folder)):
            (Path(folder) / "projects.json").write_text(json.dumps(entries), encoding="utf-8")

            return _load_projects(repos)


if __name__ == "__main__":
    unittest.main()
