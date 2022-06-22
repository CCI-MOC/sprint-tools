import click
import github
import logging

from itertools import chain

from moc_sprint_tools import cardwrapper

LOG = logging.getLogger(__name__)


@click.command(name="sort-cards-by-priority")
@click.option("--board", "-b", "selected_boards", multiple=True, default=[])
@click.pass_context
def main(ctx, selected_boards):
    sm = ctx.obj

    try:
        for board in chain(sm.open_sprints, [sm.backlog]):
            if selected_boards and board.name not in selected_boards:
                continue

            LOG.info("procssing board %s", board.name)
            for col in board.get_columns():
                LOG.info("processing column %s", col.name)
                cards = sorted(
                    cardwrapper.CardWrapper(card) for card in col.get_cards()
                )
                prev = None
                for card in cards:
                    if card.priority is None:
                        break
                    if prev is None:
                        LOG.info("move %r to top", card.title)
                        card.move("top", col)
                    else:
                        LOG.info("move %r after %r", card.title, prev.title)
                        card.move(f"after:{prev.id}", col)

                    prev = card

    except github.GithubException as err:
        raise click.ClickException(err)
