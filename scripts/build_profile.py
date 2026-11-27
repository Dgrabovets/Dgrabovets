"""Собирает SVG и README профиля из projects.json и данных GitHub"""

import json
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from profilegen import settings
from profilegen.github_client import GithubClient
from profilegen.project import Project
from profilegen.project_kind_enum import ProjectKindEnum
from profilegen.svg_render import render_badge, render_banner, render_card, render_heading, render_stats
from profilegen.theme import THEMES

# Секции списка проектов, имена совпадают с метками в README.template.md
SECTIONS = ("current", "finished")

# Значки стека: имя файла и подпись
STACK = (("csharp", "C#"), ("dotnet", ".NET"), ("aspnet-core", "ASP.NET Core"), ("ef-core", "Entity Framework Core"),
         ("sql-server", "SQL Server"), ("postgresql", "PostgreSQL"), ("kafka", "Kafka"), ("rabbitmq", "RabbitMQ"),
         ("docker", "Docker"), ("ci-cd", "CI/CD"), ("automated-tests", "Automated tests"),
         ("typescript", "TypeScript"), ("python", "Python"))

# Заголовок раздела в шаблоне: одно слово, оно же имя файла картинки. Уровень третий, потому что под вторым GitHub рисует черту,
# а черта нужна над названием: её даёт пустой `<h2></h2>` перед заголовком
HEADING_PATTERN = re.compile(r"^### (\w+)$", re.MULTILINE)

# Ширина карточки в пикселях: на широком экране две в строке, на телефоне одна во всю ширину и текст читается
CARD_DISPLAY_WIDTH = "400"

# Ширина шапки и статистики: вся страница
FULL_WIDTH = "100%"

# Альтернативные тексты картинок README
BANNER_ALT = ("Aeternus. Backend developer, C# / .NET. "
              "APIs, high-load services, integrations. Backend systems made to keep running.")
STATS_ALT = "GitHub statistics"

# Сдвиг анимации следующей карточки в секундах, чтобы соседние не двигались разом
MOTION_STAGGER = 1.7


# region Building
def _picture(path: str, alt: str, width: str = "") -> str:
    """Собирает тег `picture` со светлой и тёмной версией картинки

    Args:
        path: Путь без суффикса темы и расширения, например `assets/banner`
        alt: Альтернативный текст
        width: Ширина картинки, пусто для родного размера

    Returns:
        HTML-фрагмент
    """
    width_attribute = f' width="{width}"' if width else ""

    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{path}-dark.svg">'
            f'<img src="{path}-light.svg" alt="{escape(alt)}"{width_attribute}></picture>')


def _section_html(projects: list[Project]) -> str:
    """Собирает карточки секции без таблицы: её рамки GitHub спорят с рамками карточек

    Args:
        projects: Проекты секции

    Returns:
        Абзац с карточками-ссылками
    """
    cards = "\n".join(f'<a href="https://github.com/{settings.user()}/{project.repo}">'
                      f'{_picture(f"assets/cards/{project.repo}", f"{project.repo}: {project.description}", CARD_DISPLAY_WIDTH)}</a>'
                      for project in projects)

    return f'<p align="center">\n{cards}\n</p>'


def _load_projects(repos: dict[str, dict]) -> list[Project]:
    """Читает projects.json и дополняет язык из GitHub

    Args:
        repos: Публичные репозитории

    Returns:
        Проекты в порядке файла, поле `label` из файла берётся, только если GitHub не нашёл язык

    Raises:
        KeyError: Если репозиторий из файла не найден среди публичных или у записи нет `kind`
        ValueError: Если вид проекта неизвестен
    """
    return [Project(repo=entry["repo"],
                    section=entry["section"],
                    # Пустая строка в описании разорвала бы HTML-блок README
                    description=" ".join(entry["description"].split()),
                    label=repos[entry["repo"]]["language"] or entry.get("label", ""),
                    kind=ProjectKindEnum(entry["kind"]))
            for entry in json.loads((settings.ROOT_DIR / "projects.json").read_text(encoding="utf-8"))]


def _write(path: Path, text: str) -> None:
    """Пишет файл в UTF-8 с переводами строк LF, создавая папку

    Args:
        path: Путь к файлу
        text: Содержимое
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
# endregion Building


def main() -> None:
    """Генерирует все SVG и README"""
    client = GithubClient(settings.user(), settings.token())
    repos = client.fetch_repos()
    projects = _load_projects(repos)
    stats = client.fetch_stats(repos, settings.heatmap_weeks())
    assets = settings.assets_dir()
    readme = (settings.ROOT_DIR / "README.template.md").read_text(encoding="utf-8")
    headings = HEADING_PATTERN.findall(readme)

    for theme in THEMES:
        _write(assets / f"banner-{theme.name}.svg", render_banner(theme))
        _write(assets / f"stats-{theme.name}.svg", render_stats(stats, theme))

        for title in headings:
            _write(assets / "headings" / f"{title.lower()}-{theme.name}.svg", render_heading(title, theme))

        for slug, label in STACK:
            _write(assets / "badges" / f"{slug}-{theme.name}.svg", render_badge(label, theme))

        for index, project in enumerate(projects):
            _write(assets / "cards" / f"{project.repo}-{theme.name}.svg", render_card(project, theme, index * MOTION_STAGGER))

    readme = HEADING_PATTERN.sub(lambda match: f"### {_picture(f'assets/headings/{match[1].lower()}', match[1])}", readme)
    readme = readme.replace("{{banner}}", _picture("assets/banner", BANNER_ALT, FULL_WIDTH))
    readme = readme.replace("{{stack}}", "\n".join(_picture(f"assets/badges/{slug}", label) for slug, label in STACK))
    readme = readme.replace("{{stats}}", _picture("assets/stats", STATS_ALT, FULL_WIDTH))

    for section in SECTIONS:
        readme = readme.replace("{{" + section + "}}",
                                _section_html([project for project in projects if project.section == section]))

    _write(settings.ROOT_DIR / "README.md", readme)


if __name__ == "__main__":
    main()
