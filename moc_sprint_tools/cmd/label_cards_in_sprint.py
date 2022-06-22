import click
import github
import logging

LOG = logging.getLogger(__name__)
maybe_unlabel = {}


def process_closed_board(board):
    LOG.info('processing closed board "%s"', board.name)
    for col in board.get_columns():
        LOG.debug('processing column "%s"', col.name)
        for card in col.get_cards():
            content = card.get_content()
            if content is None:
                continue

            LOG.debug('processing card "%s"', content.title)
            if content.state == "open" and any(
                label.name == "accepted" for label in content.labels
            ):
                LOG.info(
                    'found open card "%s" on closed board "%s"',
                    content.title,
                    board.name,
                )
                maybe_unlabel[content.url] = content


def process_open_board(board):
    LOG.info('processing open board "%s"', board.name)
    for col in board.get_columns():
        LOG.debug('processing column "%s"', col.name)
        for card in col.get_cards():
            content = card.get_content()
            if content is None:
                continue

            LOG.debug('processing card "%s"', content.title)
            if any(label.name == "accepted" for label in content.labels):
                LOG.debug('card "%s" is already accepted', content.title)
            else:
                LOG.info('adding "accepted" label to card "%s"', content.title)
                content.add_to_labels("accepted")

            if content.url in maybe_unlabel:
                LOG.info(
                    'found card "%s" on open board "%s"', content.title, board.name
                )
                del maybe_unlabel[content.url]


@click.command(name="label-cards-in-sprint")
@click.pass_context
def main(ctx):
    sm = ctx.obj

    try:
        for board in sm.closed_sprints:
            process_closed_board(board)

        for board in sm.open_sprints:
            process_open_board(board)

        for url, content in maybe_unlabel.items():
            LOG.info('removing "accepted" label from card "%s"', content.title)
            content.remove_from_labels("accepted")
    except github.GithubException as err:
        raise click.ClickException(err)
