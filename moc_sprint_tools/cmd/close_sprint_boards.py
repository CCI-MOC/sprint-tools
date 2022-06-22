import click
import datetime
import github
import logging

LOG = logging.getLogger(__name__)
DEFAULT_BOARD_AGE = 28


@click.command(name="close-sprint-boards")
@click.option("--age", "-a", type=int, default=DEFAULT_BOARD_AGE)
@click.pass_context
def main(ctx, age):
    api = ctx.obj

    try:
        for board in api.open_sprints:
            now = datetime.datetime.utcnow()
            delta = now - board.created_at
            if delta.days >= age:
                LOG.info("Closing board %s", board.name)

                # LKS: we need to specify the `name` attribute here
                # until https://github.com/PyGithub/PyGithub/pull/1817
                # has merged.
                board.edit(name=board.name, state="closed")
    except github.GithubException as err:
        raise click.ClickException(err)
