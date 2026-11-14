from unittest.mock import Mock

import pytest

from jiratui.widgets.screens.context_menu import (
    ContextMenu,
    ContextMenuAction,
    ContextMenuSelection,
)


@pytest.mark.asyncio
async def test_context_menu_screen(app):
    # GIVEN
    async with app.run_test():
        screen = ContextMenu('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        options_list = screen.options_list
        assert [(o.prompt, o.id) for o in options_list.options] == [
            ('Clone Item...', 'clone_work_item'),
            ('Archive Item', 'archive_work_item'),
            ('Vote...', 'votes'),
            ('Watch...', 'watchers'),
        ]


@pytest.mark.asyncio
async def test_context_menu_screen_selection(app):
    # GIVEN
    async with app.run_test() as pilot:
        screen = ContextMenu('WI-1')
        screen.dismiss = Mock()
        # WHEN
        await app.push_screen(screen)
        await pilot.press('down')
        await pilot.press('enter')
        # THEN
        assert isinstance(screen.dismiss.call_args[0][0], ContextMenuSelection)
        assert screen.dismiss.call_args[0][0].action_id == ContextMenuAction.ARCHIVE_WORK_ITEM
        assert screen.dismiss.call_args[0][0].work_item_key == 'WI-1'
