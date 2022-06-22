import click.testing
import pytest

from unittest import mock

import moc_sprint_tools.cli
import moc_sprint_tools.sprintman


@pytest.fixture
def api(api_class, org):
    mock_api_object = mock.Mock()
    mock_api_object.organization = org
    api_class.return_value = mock_api_object

    yield mock_api_object


@pytest.fixture
def runner():
    return click.testing.CliRunner()


def test_create_sprint_boards(api, runner):
    """create new sprint board."""

    expected_title = "Sprint week 5 and 6 2021"
    expected_body = '{"week1": "2021-02-01", "week2": "2021-02-08"}'

    mock_repo = mock.Mock()
    mock_repo.get_issues.return_value = []
    api.organization.get_repo.return_value = mock_repo

    api.open_sprints = []
    api.get_sprint.side_effect = moc_sprint_tools.sprintman.BoardNotFoundError

    res = runner.invoke(moc_sprint_tools.cli.main, "create-sprint-boards -d 2021-02-01")
    assert res.exception is None
    assert res.exit_code == 0
    assert api.create_sprint.call_args_list[0][0][0] == expected_title
    assert api.create_sprint.call_args_list[0][1]["body"] == expected_body


def test_create_sprint_boards_with_duplicate(api, runner, caplog):
    """create new sprint board when one already exists with the same name"""

    expected_title = "Sprint week 5 and 6 2021"

    api.open_sprints = []
    api.get_sprint.return_value = mock.Mock()

    res = runner.invoke(moc_sprint_tools.cli.main, "create-sprint-boards -d 2021-02-01")
    assert res.exception is None
    assert res.exit_code == 0
    assert not api.create_sprint.called
    assert f'board "{expected_title}" already exists' in caplog.text


def test_create_sprint_boards_with_conflict(api, runner, caplog):
    """create new sprint board that overlaps with existing sprint board"""

    mock_repo = mock.Mock()
    mock_repo.get_issues.return_value = []
    api.organization.get_repo.return_value = mock_repo

    api.open_sprints = [
        mock.Mock(),
    ]
    api.open_sprints[0].body = '{"week1": "2021-01-22", "week2": "2021-02-08"}'
    api.open_sprints[0].name = "Test Sprint"

    api.get_sprint.side_effect = moc_sprint_tools.sprintman.BoardNotFoundError

    res = runner.invoke(moc_sprint_tools.cli.main, "create-sprint-boards -d 2021-02-01")
    assert res.exit_code == 1


def test_create_sprint_boards_with_create_issue(api, runner):
    """create new sprint board, verify new issue is created"""

    expected_issue_title = "Sprint notes for week 5 and 6 2021"

    mock_repo = mock.Mock()
    mock_repo.get_issues.return_value = []
    api.organization.get_repo.return_value = mock_repo

    api.open_sprints = []
    api.get_sprint.side_effect = moc_sprint_tools.sprintman.BoardNotFoundError

    res = runner.invoke(moc_sprint_tools.cli.main, "create-sprint-boards -d 2021-02-01")
    assert res.exception is None
    assert res.exit_code == 0
    assert mock_repo.create_issue.call_args_list[0][1]["title"] == expected_issue_title


def test_create_sprint_boards_with_existing_issue(api, runner):
    """create new sprint board, use existing notes issue"""

    mock_repo = mock.Mock(full_name="test/repo")
    mock_repo.get_issues.return_value = [
        mock.Mock(
            title="Sprint notes for week 5 and 6 2021", number=1, repository=mock_repo
        )
    ]

    api.open_sprints = []
    api.organization.get_repo.return_value = mock_repo
    api.get_sprint.side_effect = moc_sprint_tools.sprintman.BoardNotFoundError

    res = runner.invoke(moc_sprint_tools.cli.main, "create-sprint-boards -d 2021-02-01")
    assert res.exception is None
    assert res.exit_code == 0
    assert not mock_repo.create_issue.called
