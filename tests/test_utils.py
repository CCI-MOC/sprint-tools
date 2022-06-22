import click.testing
import pytest

from unittest import mock

import moc_sprint_tools.cli


@pytest.fixture
def api(api_class, org):
    mock_api_object = mock.Mock()
    mock_api_object.organization = org

    api_class.return_value = mock_api_object

    yield mock_api_object


@pytest.fixture
def runner():
    return click.testing.CliRunner()


def test_shell_no_command(api, runner):
    result = runner.invoke(moc_sprint_tools.cli.main, "shell")
    assert result.exit_code == 0


def test_shell_command(api, runner):
    result = runner.invoke(
        moc_sprint_tools.cli.main, "shell", input='print("hello world")\n'
    )
    assert result.exit_code == 0
    assert "hello world" in result.stdout


def test_boards(api, runner, projects):
    result = runner.invoke(moc_sprint_tools.cli.main, "boards")

    expected = "\n".join(project.name for project in projects)
    assert result.exit_code == 0
    assert result.stdout.strip() == expected


def test_boards_with_pattern(api, runner):
    result = runner.invoke(moc_sprint_tools.cli.main, "boards fake*")

    expected = "fake_backlog"
    assert result.exit_code == 0
    assert result.stdout.strip() == expected


def test_repos(api, runner, repos):
    result = runner.invoke(moc_sprint_tools.cli.main, "repos")

    expected = "\n".join(repo.name for repo in repos)
    assert result.exit_code == 0
    assert result.stdout.strip() == expected


def test_repos_with_pattern(api, runner):
    result = runner.invoke(moc_sprint_tools.cli.main, "repos *1")

    expected = "repo1"
    assert result.exit_code == 0
    assert result.stdout.strip() == expected
