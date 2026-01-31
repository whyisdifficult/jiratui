from unittest.mock import MagicMock, patch

import pytest

from jiratui.utils.styling import get_style_for_work_item_status, get_style_for_work_item_type


@pytest.fixture()
def mock_configuration():
    with patch('jiratui.utils.styling.CONFIGURATION') as mock_config_var:
        mock_config = MagicMock()
        mock_styling = MagicMock()
        mock_config.styling = mock_styling
        mock_config_var.get.return_value = mock_config
        yield mock_styling


@pytest.mark.parametrize(
    'status_name, expected_result',
    [
        ('done', 'green'),
        ('in review', 'dark_olive_green'),
        ('in progress', 'blue'),
        ('to do', 'yellow'),
        ('other', ''),
    ],
)
def test_get_style_for_work_item_status(mock_configuration, status_name, expected_result):
    mock_configuration.work_item_status_colors = None
    result = get_style_for_work_item_status(status_name)
    assert result == expected_result


@pytest.mark.parametrize(
    'custom_colors, status_name, expected_result',
    [
        ({'done': 'bright_green'}, 'done', 'bright_green'),  # custom overrides default
        ({'blocked': 'red'}, 'blocked', 'red'),  # custom adds new status
        ({'blocked': 'red'}, 'done', 'green'),  # default preserved when not overridden
        (None, 'done', 'green'),  # fallback to defaults when config is None
        ({'blocked': 'red'}, 'unknown_status', ''),  # unknown returns empty string
    ],
)
def test_get_style_for_work_item_status_with_custom_config(
    mock_configuration, custom_colors, status_name, expected_result
):
    mock_configuration.work_item_status_colors = custom_colors
    result = get_style_for_work_item_status(status_name)
    assert result == expected_result


@pytest.mark.parametrize(
    'type_name, expected_result',
    [
        ('bug', 'red'),
        ('epic', 'yellow'),
        ('task', 'blue'),
        ('other', ''),
    ],
)
def test_get_style_for_work_item_type(mock_configuration, type_name, expected_result):
    mock_configuration.work_item_type_colors = None
    result = get_style_for_work_item_type(type_name)
    assert result == expected_result


@pytest.mark.parametrize(
    'custom_colors, type_name, expected_result',
    [
        ({'bug': 'bright_red'}, 'bug', 'bright_red'),  # custom overrides default
        ({'story': 'cyan'}, 'story', 'cyan'),  # custom adds new type
        ({'story': 'cyan'}, 'bug', 'red'),  # default preserved when not overridden
        (None, 'bug', 'red'),  # fallback to defaults when config is None
        ({'story': 'cyan'}, 'unknown_type', ''),  # unknown returns empty string
    ],
)
def test_get_style_for_work_item_type_with_custom_config(
    mock_configuration, custom_colors, type_name, expected_result
):
    mock_configuration.work_item_type_colors = custom_colors
    result = get_style_for_work_item_type(type_name)
    assert result == expected_result
