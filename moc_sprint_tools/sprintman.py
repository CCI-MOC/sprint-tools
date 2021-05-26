import datetime
import github
import json
import logging

from functools import cached_property

from moc_sprint_tools import defaults

LOG = logging.getLogger(__name__)
DEFAULT_ORG = 'CCI-MOC'
DEFAULT_BACKLOG = 'mocbacklog'


class ApplicationError(Exception):
    pass


class BoardNotFoundError(ApplicationError):
    '''Reference to a board that does not exist.'''
    pass


class BoardConflictError(ApplicationError):
    '''Attempt to create a board that overlaps an existing board'''
    pass


class BoardExistsError(ApplicationError):
    '''Attempt to create a board with the same name as an existing board.'''


# XXX: there should probably be some error handling inside
# the sort_key helper, but the failure mode with the current code
# is "raise an exception" rather than "do the wrong thing".
def sort_sprints(sprints):
    '''return sprints sorted by start date'''

    def sort_key(sprint):
        return datetime.date.fromisoformat(
            json.loads(sprint.body)['week1'])

    return sorted(sprints, key=sort_key)


class Sprintman(github.Github):
    def __init__(self, token, org_name=None, backlog_name=None):
        super().__init__(token)
        self._org_name = org_name if org_name else DEFAULT_ORG
        self._backlog_name = backlog_name if backlog_name else DEFAULT_BACKLOG

    @cached_property
    def organization(self):
        return self.get_organization(self._org_name)

    @property
    def open_sprints(self):
        for board in self.organization.get_projects('open'):
            if board.name.lower().strip().startswith('sprint'):
                yield board

    def get_sprint(self, name):
        for board in self.open_sprints:
            if board.name.lower() == name.lower():
                return board
        raise BoardNotFoundError(name)

    @property
    def closed_sprints(self):
        for board in self.organization.get_projects('closed'):
            if board.name.lower().startswith('sprint'):
                yield board

    @property
    def backlog(self):
        for board in self.organization.get_projects('open'):
            if board.name.lower() == self._backlog_name.lower():
                break
        else:
            raise BoardNotFoundError(self._backlog_name)

        return board

    def get_column(self, board, name):
        for c in board.get_columns():
            if c.name.lower() == name.lower():
                return c

    def create_sprint(self, name, body=None):
        board = self.organization.create_project(name, body=body)
        board.edit(private=False)

        for column in defaults.default_sprint_columns:
            LOG.debug('adding column %s in board %s', column, name)
            board.create_column(column)

        return board

    def copy_card(self, source_card, destination_column):
        content = source_card.get_content()

        try:
            if content:
                if isinstance(content, github.Issue.Issue):
                    content_type = 'Issue'
                elif isinstance(content, github.PullRequest.PullRequest):
                    content_type = 'PullRequest'
                else:
                    LOG.warning("couldn't copy card %s with unkown type", source_card)
                    return

                LOG.info('adding card "%s" to column %s',
                         content.title,
                         destination_column.name)
                destination_column.create_card(
                    content_id=content.id,
                    content_type=content_type,
                )
            elif source_card.note:
                destination_column.create_card(note=source_card.note)
            else:
                raise ValueError(f'card {source_card.id} has no content')
        except github.GithubException as err:
            # XXX: we can make the error display nicer by parsing out the
            # content of err.data['errors'].
            LOG.warning('failed to copy card %s: %s', source_card, err)

    def copy_board(self, source_board, destination_board,
                   columns=None, ignore_columns=None):

        if columns is None:
            columns = source_board.get_columns()

        if ignore_columns is None:
            ignore_columns = defaults.default_skip_copy

        for source in columns:
            LOG.debug('copying cards from column %s', source.name)
            if source.name.lower() in ignore_columns:
                continue

            destination = self.get_column(destination_board, source.name)
            if destination is None:
                destination = destination_board.create_column(source.name)

            cards = list(source.get_cards())

            for card in reversed(cards):
                LOG.debug('copying card %s', card.id)
                self.copy_card(card, destination)
