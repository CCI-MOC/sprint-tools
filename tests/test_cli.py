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


def test_main_invalid_args(runner):
    res = runner.invoke(moc_sprint_tools.cli.main, "invalid")
    assert res.exit_code == 2


def test_main_override_org(api_class, runner):
    res = runner.invoke(moc_sprint_tools.cli.main, "-o fake_org shell")
    assert res.exit_code == 0
    assert api_class.call_args[1]["org_name"] == "fake_org"
