import click
import csv
import datetime
import github
import logging

from moc_sprint_tools.sprintman import BoardNotFoundError

LOG = logging.getLogger(__name__)


def load_sprint_data(input_file):
    sprints = []
    with open(input_file) as f:
        reader = csv.reader(f)
        next(f)
        for row in reader:
            sprints.append(
                [row[0], datetime.datetime.strptime(row[1], '%Y-%m-%d')])
    return sprints


@click.command(name='create-sprint-boards')
@click.option('--file', '-f', type=str, default='./config/sprint_dates.csv')
@click.option('--copy-cards/--no-copy-cards', default=True)
@click.pass_context
def main(ctx, file, copy_cards):
    api = ctx.obj

    try:
        sprints = load_sprint_data(file)
        current_sprint = None
        previous_sprint = None
        today = datetime.datetime.utcnow()

        for line, sprint in enumerate(sorted(sprints, key=lambda x: x[1])):
            if today > sprint[1]:
                current_sprint = sprint

                if line > 0:
                    previous_sprint = sprints[line - 1]
            else:
                break

        if not current_sprint:
            LOG.warning('No sprint is current')
            return

        try:
            api.get_sprint(current_sprint[0])
            LOG.warning('Sprint board "%s" already exists.' % current_sprint[0])
            return
        except BoardNotFoundError:
            board = api.create_sprint(current_sprint[0])

            if previous_sprint and copy_cards:
                try:
                    previous_board = api.get_sprint(previous_sprint[0])
                    api.copy_board(previous_board, board)
                except BoardNotFoundError:
                    LOG.error('previous sprint board %s does not exist', previous_sprint[0])

    except github.GithubException as err:
        raise click.ClickException(err)
