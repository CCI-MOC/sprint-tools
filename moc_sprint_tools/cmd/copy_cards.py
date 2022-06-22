import click
import logging

from moc_sprint_tools.sprintman import sort_sprints, BoardNotFoundError

LOG = logging.getLogger(__name__)


def CommaDelimitedList(val):
    if val is None:
        return None

    return val.split(",")


@click.command(name="copy-cards")
@click.option("-f", "--from", "src", metavar="BOARD_NAME")
@click.option("-t", "--to", "dst", metavar="BOARD_NAME")
@click.option("-c", "--copy-columns", type=CommaDelimitedList)
@click.option("-i", "--ignore-columns", type=CommaDelimitedList)
@click.option("-I", "--no-default-ignore", is_flag=True)
@click.pass_context
def main(ctx, src, dst, copy_columns, ignore_columns, no_default_ignore):
    api = ctx.obj

    if not (src and dst):
        raise click.ClickException(
            "you must provide both a source and destination board"
        )

    if ignore_columns is None and no_default_ignore:
        ignore_columns = []

    sprints = sort_sprints(api.open_sprints)

    def resolve_sprint(name):
        if name.lower() in ["cur", "current", "latest"]:
            return sprints[-1]
        elif name.lower() in ["prev", "previous"]:
            return sprints[-2]
        else:
            return api.get_sprint(name)

    try:
        src_board = resolve_sprint(src)
        dst_board = resolve_sprint(dst)
    except BoardNotFoundError as err:
        raise click.ClickException(f"no board named {err}")

    LOG.info("copying cards from %s -> %s", src_board.name, dst_board.name)

    api.copy_board(
        src_board, dst_board, columns=copy_columns, ignore_columns=ignore_columns
    )
