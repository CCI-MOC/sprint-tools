from unittest import mock

import moc_sprint_tools.cardwrapper


def test_cardwrapper_note_set_priority():
    card = mock.Mock()
    card.note = "This is a test"
    wrapped = moc_sprint_tools.cardwrapper.CardWrapper(card)
    wrapped.priority = 0
    assert wrapped.edit.call_args_list[0][1]["note"] == "[0] This is a test"


def test_cardwrapper_note_set_title():
    card = mock.Mock()
    card.note = "[0] This is a test"
    wrapped = moc_sprint_tools.cardwrapper.CardWrapper(card)
    wrapped.title = "This was a test"
    assert wrapped.edit.call_args_list[0][1]["note"] == "[0] This was a test"


def test_cardwrapper_note_get_priority():
    card = mock.Mock()
    card.note = "[0] This is a test"
    wrapped = moc_sprint_tools.cardwrapper.CardWrapper(card)
    assert wrapped.priority == 0


def test_cardwrapper_note_change_priority():
    card = mock.Mock()
    card.note = "[0] This is a test"
    wrapped = moc_sprint_tools.cardwrapper.CardWrapper(card)
    wrapped.priority = 1
    assert wrapped.edit.call_args_list[0][1]["note"] == "[1] This is a test"


def test_cardwrapper_content_set_priority():
    content = mock.Mock()
    content.title = "This is a test"
    card = mock.Mock()
    card.note = None
    card.get_content.return_value = content
    wrapped = moc_sprint_tools.cardwrapper.CardWrapper(card)
    wrapped.priority = 0
    assert content.edit.call_args_list[0][1]["title"] == "[0] This is a test"


def test_cardwrapper_content_change_priority():
    content = mock.Mock()
    content.title = "[0] This is a test"
    card = mock.Mock()
    card.note = None
    card.get_content.return_value = content
    wrapped = moc_sprint_tools.cardwrapper.CardWrapper(card)
    wrapped.priority = 1
    assert content.edit.call_args_list[0][1]["title"] == "[1] This is a test"


def test_cardwrapper_content_get_priority():
    content = mock.Mock()
    content.title = "[0] This is a test"
    card = mock.Mock()
    card.note = None
    card.get_content.return_value = content
    wrapped = moc_sprint_tools.cardwrapper.CardWrapper(card)
    assert wrapped.priority == 0


def test_cardwrapper_sort():
    def _make_card(title, id):
        card = mock.Mock()
        card.id = id
        card.note = title
        wrapped = moc_sprint_tools.cardwrapper.CardWrapper(card)
        return wrapped

    cardA = _make_card("Card A", 1234)
    cardB = _make_card("[0] Card B", 2345)
    cardC = _make_card("[1] Card C", 3456)

    cards = [cardA, cardB, cardC]
    sorted_cards = sorted(cards)
    assert sorted_cards == [cardB, cardC, cardA]
