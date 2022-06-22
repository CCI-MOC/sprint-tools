import pytest

from unittest import mock

import moc_sprint_tools.sprintman
import moc_sprint_tools.defaults


@pytest.fixture
def api(org):
    api = moc_sprint_tools.sprintman.Sprintman(
        "fake_token",
        org_name="fake_org",
        backlog_name="fake_backlog",
    )

    api.get_organization = mock.Mock()
    api.get_organization.return_value = org

    return api


def test_organization(api):
    api.get_organization = mock.Mock()
    api.organization

    assert api.get_organization.call_args == (("fake_org",),)


def test_open_sprints(api):
    res = list(api.open_sprints)
    assert len(res) == 1
    assert res[0].name == "sprint project1"


def test_closed_sprints(api):
    res = list(api.closed_sprints)
    assert len(res) == 1
    assert res[0].name == "sprint project2"


def test_backlog(api):
    res = api.backlog
    assert res.name == "fake_backlog"


def test_get_sprint(api, projects):
    res = api.get_sprint("sprint project1")
    assert res == projects[0]


def test_get_sprint_missing_board(api):
    with pytest.raises(moc_sprint_tools.sprintman.BoardNotFoundError):
        api.get_sprint("missing sprint")


def test_create_sprint(api, org):
    mock_project = mock.Mock()
    org.create_project.return_value = mock_project

    api.create_sprint("sprint test")
    assert org.create_project.called_with("sprint test")
    assert [(x,) for x in moc_sprint_tools.defaults.default_sprint_columns] == [
        x[0] for x in mock_project.create_column.call_args_list
    ]
