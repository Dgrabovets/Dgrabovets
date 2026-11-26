"""Клиент GitHub API"""

import json
import urllib.request

from .profile_stats import ProfileStats

# Адрес REST API
API_URL = "https://api.github.com"

# Лимит страницы списка репозиториев в REST API
REPOS_PAGE_SIZE = 100

# Таймаут запроса к API в секундах, чтобы сборка не зависала при сбое сети
REQUEST_TIMEOUT_SECONDS = 30

# Сколько языков показывать в полосе
TOP_LANGUAGES = 5

# Запрос вклада за последний год и календаря активности
CONTRIBUTIONS_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar { weeks { contributionDays { contributionCount } } }
    }
  }
}
"""


class GithubClient:
    """Читает репозитории, языки и вклад владельца"""

    def __init__(self, user: str, token: str) -> None:
        """Создаёт клиент

        Args:
            user: Логин владельца
            token: Токен GitHub
        """
        self._user = user
        self._token = token

    # region Public
    def fetch_repos(self) -> dict[str, dict]:
        """Читает публичные репозитории владельца

        Returns:
            Словарь «имя репозитория → данные API»
        """
        return {repo["name"]: repo
                for repo in self._get(f"/users/{self._user}/repos?per_page={REPOS_PAGE_SIZE}&type=owner")}

    def fetch_stats(self, repos: dict[str, dict], weeks_count: int) -> ProfileStats:
        """Собирает статистику профиля

        Args:
            repos: Публичные репозитории, результат `fetch_repos`
            weeks_count: Сколько последних недель взять в график

        Returns:
            Статистика для блока на странице профиля
        """
        collection = self._graphql(CONTRIBUTIONS_QUERY,
                                   {"login": self._user})["data"]["user"]["contributionsCollection"]
        return ProfileStats(commits=collection["totalCommitContributions"],
                            pull_requests=collection["totalPullRequestContributions"],
                            languages=self._fetch_languages(repos),
                            weeks=[[day["contributionCount"] for day in week["contributionDays"]]
                               for week in collection["contributionCalendar"]["weeks"]][-weeks_count:])
    # endregion Public

    # region Private
    def _fetch_languages(self, repos: dict[str, dict]) -> list[tuple[str, float]]:
        """Считает доли языков по байтам в собственных репозиториях

        Args:
            repos: Публичные репозитории

        Returns:
            Пары «язык, доля в процентах», самые крупные первыми
        """
        totals: dict[str, int] = {}

        for name, repo in repos.items():
            if repo["fork"]:
                continue

            for language, size in self._get(f"/repos/{self._user}/{name}/languages").items():
                totals[language] = totals.get(language, 0) + size

        whole = sum(totals.values()) or 1

        return [(language, size * 100 / whole)
                for language, size in sorted(totals.items(), key=lambda pair: pair[1], reverse=True)[:TOP_LANGUAGES]]

    def _request(self, url: str, body: bytes | None = None) -> object:
        """Выполняет запрос к API

        Args:
            url: Полный адрес
            body: Тело POST-запроса, для GET пусто

        Returns:
            Разобранный JSON ответа
        """
        headers = {"Authorization": f"Bearer {self._token}", "Accept": "application/vnd.github+json"}

        with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers),
                                    timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.load(response)

    def _get(self, path: str) -> object:
        """Выполняет GET к REST API

        Args:
            path: Путь с параметрами, начиная с `/`

        Returns:
            Разобранный JSON ответа
        """
        return self._request(f"{API_URL}{path}")

    def _graphql(self, query: str, variables: dict) -> dict:
        """Выполняет запрос GraphQL

        Args:
            query: Текст запроса
            variables: Переменные запроса

        Returns:
            Ответ API целиком
        """
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")

        return self._request(f"{API_URL}/graphql", payload)
    # endregion Private
