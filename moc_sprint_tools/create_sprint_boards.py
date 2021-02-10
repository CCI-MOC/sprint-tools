import click
import csv
import datetime
import github
import logging

from moc_sprint_tools.sprintman import BoardNotFoundError

LOG = logging.getLogger(__name__)

CARD_COPYING_MAP = {
    'notes': 'notes',
    'backlog': 'backlog',
    'in progress': 'in progress'
}


def load_sprint_data(input_file):
    sprints = []
    with open(input_file) as f:
        reader = csv.reader(f)
        next(f)
        for row in reader:
            sprints.append(
                [row[0], datetime.datetime.strptime(row[1], '%Y-%m-%d')])
    return sprints


def get_column(board, name):
    for c in board.get_columns():
        if c.name.lower() == name.lower():
            return c


def copy_card(source_card, destination_column):
    content = source_card.get_content()
    if content:
        if isinstance(content, github.Issue.Issue):
            content_type = 'Issue'
        elif isinstance(content, github.PullRequest.PullRequest):
            content_type = 'PullRequest'
        else:
            LOG.warning('Couldn\'t copy card with unkown type')
            return

        LOG.info('adding card "%s" to %s', (content.title,
                                            destination_column.name))
        destination_column.create_card(
            content_id=content.id,
            content_type=content_type,
        )
    else:
        destination_column.create_card(note=source_card.note)


def copy_board(source_board, destination_board):
    for source in source_board.get_columns():
        destination = CARD_COPYING_MAP.get(source.name.lower(), None)
        if not destination:
            continue

        destination = get_column(destination_board, destination)
        cards = list(source.get_cards())
        cards.reverse()  # Creating a card adds it to the top

        for card in cards:
            copy_card(card, destination)


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
        for line, sprint in enumerate(sprints):
            today = datetime.datetime.utcnow()
            if today > sprint[1]:
                current_sprint = sprint

                if line > 0:
                    previous_sprint = sprints[line - 1]
                break

        if not current_sprint:
            LOG.warning('No sprint is current')
            return

        try:
            api.get_sprint(current_sprint[0])
            LOG.debug('Sprint board "%s" already exists.' % current_sprint[0])
            return
        except BoardNotFoundError:
            board = api.create_sprint(current_sprint[0])

            if previous_sprint and copy_cards:
                previous_board = api.get_sprint(previous_sprint[0])
                copy_board(previous_board, board)

    except github.GithubException as err:
        raise click.ClickException(err)
