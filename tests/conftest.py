import pytest

from dataclasses import dataclass
from unittest import mock


@dataclass
class FakeProject:
    name: str
    state: str


@dataclass
class FakeRepo:
    name: str


@pytest.fixture
def api_class():
    with mock.patch("moc_sprint_tools.cli.Sprintman") as mock_api:
        yield mock_api


@pytest.fixture
def projects():
    return [
        FakeProject(name="sprint project1", state="open"),
        FakeProject(name="sprint project2", state="closed"),
        FakeProject(name="fake_backlog", state="open"),
    ]


@pytest.fixture
def repos():
    return [
        FakeRepo(name="repo1"),
        FakeRepo(name="repo2"),
    ]


@pytest.fixture
def org(projects, repos):
    def _get_repos():
        return repos

    def _get_projects(state=None):
        return [
            project for project in projects if state is None or project.state == state
        ]

    fake_org = mock.Mock()
    fake_org.get_projects = _get_projects
    fake_org.get_repos = _get_repos
    return fake_org
