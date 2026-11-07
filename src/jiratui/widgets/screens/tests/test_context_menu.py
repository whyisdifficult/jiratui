from unittest.mock import Mock

import pytest

from jiratui.widgets.screens.context_menu import (
    WorkItemContextMenu,
    WorkItemContextMenuOptionAction,
    WorkItemContextMenuSelection,
)


@pytest.mark.asyncio
async def test_context_menu_screen(app):
    # GIVEN
    async with app.run_test():
        screen = WorkItemContextMenu('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        options_list = screen.options_list
        assert [(o.prompt, o.id) for o in options_list.options] == [
            ('Clone Work Item', 'clone_work_item'),
            ('Archive Work Item', 'archive_work_item'),
        ]


@pytest.mark.asyncio
async def test_context_menu_screen_selection(app):
    # GIVEN
    async with app.run_test() as pilot:
        screen = WorkItemContextMenu('WI-1')
        screen.dismiss = Mock()
        # WHEN
        await app.push_screen(screen)
        await pilot.press('down')
        await pilot.press('enter')
        # THEN
        assert isinstance(screen.dismiss.call_args[0][0], WorkItemContextMenuSelection)
        assert (
            screen.dismiss.call_args[0][0].action_id
            == WorkItemContextMenuOptionAction.ARCHIVE_WORK_ITEM
        )
        assert screen.dismiss.call_args[0][0].work_item_key == 'WI-1'
