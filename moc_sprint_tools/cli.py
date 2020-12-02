import click
import github
import logging
import os

from moc_sprint_tools import defaults
from moc_sprint_tools import label_cards_in_sprint
from moc_sprint_tools import label_needs_description
from moc_sprint_tools import sort_cards_by_priority
from moc_sprint_tools.sprintman import Sprintman


@click.group()
@click.option('-v', '--verbose', count=True, type=int)
@click.option('-o', '--organization', default=defaults.default_organization)
@click.pass_context
def main(ctx, verbose, organization):
    try:
        loglevel = ['WARNING', 'INFO', 'DEBUG'][verbose]
    except IndexError:
        loglevel = 'DEBUG'

    logging.basicConfig(level=loglevel)

    try:
        ctx.obj = Sprintman(os.environ.get('GH_API_TOKEN'),
                            org_name=organization)
    except github.GithubException as err:
        raise click.ClickException(err)


main.add_command(label_cards_in_sprint.main)
main.add_command(label_needs_description.main)
main.add_command(sort_cards_by_priority.main)
