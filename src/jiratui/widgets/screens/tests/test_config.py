from unittest.mock import Mock, patch

import pytest
from textual.widgets import TextArea

from jiratui.widgets.screen import MainScreen
from jiratui.widgets.screens.config import ConfigFileScreen, ConfigTable


@patch.object(ConfigFileScreen, '_get_config_data')
@pytest.mark.asyncio
async def test_config_screen(get_config_data: Mock, app):
    # GIVEN
    get_config_data.return_value = {
        'styling': {'field_a': 'value a'},
        'setting_a': True,
        'setting_b': 1,
        'setting_c': 'value c',
    }
    async with app.run_test():
        screen = ConfigFileScreen()
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.datatable_config_info.row_count == 4


@patch.object(ConfigFileScreen, '_get_config_data')
@pytest.mark.asyncio
async def test_config_screen_select_row_opens_right_panel(get_config_data: Mock, app):
    # GIVEN
    get_config_data.return_value = {
        'styling': {'field_a': 'value a'},
        'setting_a': True,
    }
    async with app.run_test() as pilot:
        screen = ConfigFileScreen()
        # WHEN
        await app.push_screen(screen)
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('tab')
        # THEN
        assert isinstance(app.focused, TextArea)


@patch.object(ConfigFileScreen, '_get_config_data')
@pytest.mark.asyncio
async def test_config_screen_deselect_row_closes_right_panel(get_config_data: Mock, app):
    # GIVEN
    get_config_data.return_value = {
        'styling': {'field_a': 'value a'},
        'setting_a': True,
    }
    async with app.run_test() as pilot:
        screen = ConfigFileScreen()
        # WHEN
        await app.push_screen(screen)
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('escape')
        # THEN
        assert isinstance(app.focused, ConfigTable)


@patch.object(ConfigFileScreen, '_get_config_data')
@pytest.mark.asyncio
async def test_config_screen_select_non_json_row_does_not_open_right_panel(
    get_config_data: Mock, app
):
    # GIVEN
    get_config_data.return_value = {
        'setting_a': True,
        'styling': {'field_a': 'value a'},
    }
    async with app.run_test() as pilot:
        screen = ConfigFileScreen()
        # WHEN
        await app.push_screen(screen)
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        assert isinstance(app.focused, ConfigTable)


@patch.object(ConfigFileScreen, '_get_config_data')
@pytest.mark.asyncio
async def test_config_screen_dismiss(get_config_data: Mock, app):
    # GIVEN
    get_config_data.return_value = {
        'setting_a': True,
        'styling': {'field_a': 'value a'},
    }
    async with app.run_test() as pilot:
        screen = ConfigFileScreen()
        # WHEN
        await app.push_screen(screen)
        await pilot.press('escape')
        # THEN
        assert isinstance(app.screen, MainScreen)
