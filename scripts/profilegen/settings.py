"""Настройки сборки профиля, читаются из окружения и файла .env"""

import os
from pathlib import Path

# Корень репозитория профиля: на два уровня выше этого файла
ROOT_DIR = Path(__file__).resolve().parents[2]


# region Reading
def _read_env_file() -> dict[str, str]:
    """Читает пары ключ=значение из .env в корне

    Returns:
        Словарь значений, пустой, если файла нет
    """
    path = ROOT_DIR / ".env"
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()

        if not text or text.startswith("#") or "=" not in text:
            continue

        key, value = text.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def _read(name: str, default: str) -> str:
    """Читает настройку: окружение, затем .env, затем значение по умолчанию

    Args:
        name: Имя переменной
        default: Значение, если переменная не задана

    Returns:
        Значение настройки
    """
    return os.environ.get(name) or _read_env_file().get(name) or default


def user() -> str:
    """Читает логин владельца профиля

    Returns:
        Логин GitHub
    """
    return _read("PROFILE_USER", "Dgrabovets")


def assets_dir() -> Path:
    """Читает папку для SVG

    Returns:
        Путь к папке внутри репозитория
    """
    return ROOT_DIR / _read("PROFILE_ASSETS_DIR", "assets")


def fonts_dir() -> Path:
    """Читает папку шрифтов бренда для `extract_glyphs.py`

    Returns:
        Путь к папке с файлами шрифтов
    """
    return ROOT_DIR / _read("PROFILE_FONTS_DIR", "fonts")


def heatmap_weeks() -> int:
    """Читает число недель в графике активности

    Returns:
        Число недель
    """
    return int(_read("PROFILE_HEATMAP_WEEKS", "40"))


def token() -> str:
    """Читает токен GitHub

    Returns:
        Токен доступа

    Raises:
        RuntimeError: Если GITHUB_TOKEN не задан
    """
    value = _read("GITHUB_TOKEN", "")

    if not value:
        raise RuntimeError("GITHUB_TOKEN не задан, локально: $env:GITHUB_TOKEN = gh auth token")

    return value
# endregion Reading
