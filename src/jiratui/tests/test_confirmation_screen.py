from unittest.mock import Mock

import pytest
from textual.widgets import Label

from jiratui.widgets.screens.confirmation import ConfirmationScreen


@pytest.mark.parametrize(
    'input_message, expected_message',
    [
        ('show this message', 'show this message'),
        ('', 'Are you sure you want to perform this action?'),
        (None, 'Are you sure you want to perform this action?'),
    ],
)
@pytest.mark.asyncio
async def test_open_confirmation_screen(input_message: str, expected_message: str, app):
    async with app.run_test():
        # WHEN
        widget = ConfirmationScreen(input_message)
        await app.push_screen(widget)
        await app.workers.wait_for_complete()
        # THEN
        assert isinstance(app.screen, ConfirmationScreen)
        label = widget.query_one(Label)
        assert label.content == expected_message


@pytest.mark.asyncio
async def test_open_confirmation_screen_press_cancel(app):
    async with app.run_test() as pilot:
        # GIVEN
        screen = ConfirmationScreen('hello?')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        assert isinstance(app.screen, ConfirmationScreen)
        # WHEN
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        assert not screen.dismiss.call_args[0][0]


@pytest.mark.asyncio
async def test_open_confirmation_screen_press_accept(app):
    async with app.run_test() as pilot:
        # GIVEN
        screen = ConfirmationScreen('hello?')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        assert isinstance(app.screen, ConfirmationScreen)
        # WHEN
        await pilot.press('enter')
        # THEN
        assert screen.dismiss.call_args[0][0]
