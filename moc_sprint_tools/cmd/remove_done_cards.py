import click
import datetime
import github
import logging

from moc_sprint_tools import defaults

LOG = logging.getLogger(__name__)


@click.command(name='remove-done-cards')
@click.option('--days', '-d', type=int, default=defaults.default_days_done)
@click.pass_context
def main(ctx, days):
    api = ctx.obj
    delta = datetime.timedelta(days=days)
    now = datetime.datetime.utcnow()

    try:
        done = next(
            x for x in api.backlog.get_columns() if x.name.lower() == 'done'
        )

        for card in done.get_cards():
            if card.note:
                LOG.debug("skipping note")
                continue

            content = card.get_content()
            if not content.closed_at:
                LOG.debug('skipping "%s" (not closed)', content.title)
                continue

            if now - content.closed_at < delta:
                LOG.debug('skipping "%s" (too recent)', content.title)
                continue

            LOG.info('removing "%s" from project', content.title)
            card.delete()
    except github.GithubException as err:
        raise click.ClickException(err)
