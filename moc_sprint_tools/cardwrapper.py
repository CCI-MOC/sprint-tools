import jinja2
import re

re_priority = re.compile(r"(\[\s*(?P<prio>\d+)\s*\]\s*)?(?P<title>.*)")
title_format = jinja2.Template(
    "{% if priority is not none %}[{{ priority }}] {% endif %}{{ title }}"
)


class CardWrapper:
    def __init__(self, card):
        self.card = card

    def __getattr__(self, k):
        return getattr(self.card, k)

    def __repr__(self):
        title = self.title.splitlines()[0][:40].strip()
        return f'<title="{title}" priority={self.priority} id={self.id}>'

    def __lt__(self, other):
        if self.priority is None:
            return False
        elif other.priority is None:
            return True
        else:
            return self.priority < other.priority

    @property
    def _raw_title(self):
        if self.note:
            title = self.note.splitlines()[0]
        else:
            content = self.get_content()
            title = content.title

        return title

    @_raw_title.setter
    def _raw_title(self, title):
        if self.note:
            lines = self.note.splitlines()
            lines[0] = title
            note = "\n".join(lines)
            self.edit(note=note)
        else:
            content = self.get_content()
            content.edit(title=title)

    @property
    def title(self):
        mo = re_priority.match(self._raw_title)
        return mo.group("title")

    @title.setter
    def title(self, title):
        self.set_priority_and_title(self.priority, title)

    @property
    def priority(self):
        mo = re_priority.match(self._raw_title)
        prio = mo.group("prio")
        return int(prio) if prio is not None and prio.isdigit() else None

    @priority.setter
    def priority(self, priority):
        self.set_priority_and_title(priority, self.title)

    def set_priority_and_title(self, priority, title):
        self._raw_title = title_format.render(
            title=title,
            priority=priority,
        )
