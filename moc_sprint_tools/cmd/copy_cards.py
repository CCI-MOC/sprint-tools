import click
import github
import logging

from moc_sprint_tools.sprintman import BoardNotFoundError
from moc_sprint_tools import defaults

LOG = logging.getLogger(__name__)


def CommaDelimitedList(val):
    if val is None:
        return None

    return val.split(',')


@click.command(name='copy-cards')
@click.option('-f', '--from', 'src', metavar='BOARD_NAME')
@click.option('-t', '--to', 'dst', metavar='BOARD_NAME')
@click.option('-c', '--copy-columns', type=CommaDelimitedList)
@click.option('-i', '--ignore-columns', type=CommaDelimitedList)
@click.option('-I', '--no-default-ignore', is_flag=True)
@click.pass_context
def main(ctx, src, dst, copy_columns, ignore_columns, no_default_ignore):
    api = ctx.obj

    if not (src and dst):
        raise click.ClickException('you must provide both a source and destination board')

    if ignore_columns is None:
        if no_default_ignore:
            ignore_columns = []

    try:
        src_board = api.get_sprint(src)
        dst_board = api.get_sprint(dst)
    except BoardNotFoundError as err:
        raise click.ClickException(f'no board named {err}')

    LOG.info('copying cards from %s -> %s', src_board.name, dst_board.name)
    api.copy_board(src_board, dst_board,
                   columns=copy_columns,
                   ignore_columns=ignore_columns)
