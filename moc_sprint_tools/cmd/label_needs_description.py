import click
import github
import logging

LOG = logging.getLogger(__name__)


@click.command(name="label-needs-description")
@click.pass_context
def main(ctx):
    sm = ctx.obj

    try:
        for col in sm.backlog.get_columns():
            for card in col.get_cards():
                content = card.get_content()
                if not content:
                    continue

                if not content.body and not any(
                    label.name == "needs_description" for label in content.labels
                ):
                    LOG.info('card "%s" has no description', content.title)
                    content.add_to_labels("needs_description")
                elif content.body and any(
                    label.name == "needs_description" for label in content.labels
                ):
                    LOG.info('card "%s" has added a description', content.title)
                    content.remove_from_labels("needs_description")

    except github.GithubException as err:
        raise click.ClickException(f"{err}")
