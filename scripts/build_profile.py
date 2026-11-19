"""Собирает SVG и README профиля из projects.json и данных GitHub"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from profilegen import settings
from profilegen.github_client import GithubClient
from profilegen.project import Project
from profilegen.svg_render import render_banner, render_card, render_stats
from profilegen.theme import THEMES

# Секции списка проектов, имена совпадают с метками в README.template.md
SECTIONS = ("current", "finished")

# Сколько карточек в строке сетки
CARDS_PER_ROW = 2

# Ячейка сетки: ширина делится поровну между карточками строки
CELL_OPEN = '<td width="50%">'

# Альтернативные тексты картинок README
BANNER_ALT = "Aeternus, backend developer, C# and .NET"
STATS_ALT = "GitHub statistics"


# region Building
def _picture(path: str, alt: str) -> str:
    """Собирает тег `picture` со светлой и тёмной версией картинки

    Args:
        path: Путь без суффикса темы и расширения, например `assets/banner`
        alt: Альтернативный текст

    Returns:
        HTML-фрагмент
    """
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{path}-dark.svg">'
            f'<img src="{path}-light.svg" alt="{alt}" width="100%"></picture>')


def _section_html(projects: list[Project]) -> str:
    """Собирает сетку карточек секции

    Args:
        projects: Проекты секции

    Returns:
        HTML-таблица со ссылками на репозитории
    """
    cells = [f'{CELL_OPEN}<a href="https://github.com/{settings.user()}/{project.repo}">'
             f'{_picture(f"assets/cards/{project.repo}", project.repo)}</a></td>'
             for project in projects]

    while len(cells) % CARDS_PER_ROW:
        cells.append(f"{CELL_OPEN}</td>")

    return "<table>\n" + "\n".join("<tr>" + "".join(cells[index:index + CARDS_PER_ROW]) + "</tr>"
                                   for index in range(0, len(cells), CARDS_PER_ROW)) + "\n</table>"


def _load_projects(repos: dict[str, dict]) -> list[Project]:
    """Читает projects.json и дополняет язык и звёзды из GitHub

    Args:
        repos: Публичные репозитории

    Returns:
        Проекты в порядке файла

    Raises:
        KeyError: Если репозиторий из файла не найден среди публичных
    """
    return [Project(repo=entry["repo"],
                    section=entry["section"],
                    description=entry["description"],
                    language=repos[entry["repo"]]["language"] or "",
                    stars=repos[entry["repo"]]["stargazers_count"])
            for entry in json.loads((settings.ROOT_DIR / "projects.json").read_text(encoding="utf-8"))]


def _write(path: Path, text: str) -> None:
    """Пишет файл в UTF-8 с переводами строк LF

    Args:
        path: Путь к файлу
        text: Содержимое
    """
    path.write_text(text, encoding="utf-8", newline="\n")
# endregion Building


def main() -> None:
    """Генерирует все SVG и README"""
    client = GithubClient(settings.user(), settings.token())
    repos = client.fetch_repos()
    projects = _load_projects(repos)
    stats = client.fetch_stats(repos, settings.heatmap_weeks())
    assets = settings.assets_dir()
    (assets / "cards").mkdir(parents=True, exist_ok=True)

    for theme in THEMES:
        _write(assets / f"banner-{theme.name}.svg", render_banner(theme))
        _write(assets / f"stats-{theme.name}.svg", render_stats(stats, theme))

        for project in projects:
            _write(assets / "cards" / f"{project.repo}-{theme.name}.svg", render_card(project, theme))

    readme = (settings.ROOT_DIR / "README.template.md").read_text(encoding="utf-8")
    readme = readme.replace("{{banner}}", _picture("assets/banner", BANNER_ALT))
    readme = readme.replace("{{stats}}", _picture("assets/stats", STATS_ALT))

    for section in SECTIONS:
        readme = readme.replace("{{" + section + "}}",
                                _section_html([project for project in projects if project.section == section]))

    _write(settings.ROOT_DIR / "README.md", readme)


if __name__ == "__main__":
    main()
