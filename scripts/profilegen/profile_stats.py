"""Сводная статистика владельца"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileStats:
    """Числа и графики для блока статистики"""

    stars: int
    commits: int
    pull_requests: int
    languages: list[tuple[str, float]]
    weeks: list[list[int]]
