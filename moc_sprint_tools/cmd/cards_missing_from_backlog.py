import click
import github
import logging

LOG = logging.getLogger(__name__)


def get_all_cards(board):
    cards = {}

    LOG.info('getting cards from board "%s"', board.name)
    for col in board.get_columns():
        if col.name.lower() in ["notes"]:
            continue

        LOG.debug('processing column "%s"', col.name)
        for card in col.get_cards():
            content = card.get_content()
            if content is None:
                continue

            LOG.debug('processing card "%s"', content.title)
            cards[content.url] = content

    return cards


def find_missing_cards(board, all_cards):
    cards = get_all_cards(board)
    new_cards = {}

    for url, content in cards.items():
        if url not in all_cards:
            LOG.info('card "%s" not in backlog', content.title)
            new_cards[url] = content

    return new_cards


@click.command(name="cards-missing-from-backlog")
@click.pass_context
def main(ctx):
    api = ctx.obj

    try:
        backlog = next(
            x for x in api.backlog.get_columns() if x.name.lower() == "backlog"
        )

        all_cards = get_all_cards(api.backlog)
        new_cards = {}
        for board in api.open_sprints:
            new_cards.update(find_missing_cards(board, all_cards))

        for content in new_cards.values():
            if isinstance(content, github.Issue.Issue):
                content_type = "Issue"
            elif isinstance(content, github.PullRequest.PullRequest):
                content_type = "PullRequest"
            else:
                raise ValueError(type(content))

            LOG.info('adding card "%s" to backlog', content.title)
            backlog.create_card(
                content_id=content.id,
                content_type=content_type,
            )

    except github.GithubException as err:
        raise click.ClickException(err)
