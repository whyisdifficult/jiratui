import pytest

from jiratui.utils.styling import get_style_for_work_item_status, get_style_for_work_item_type


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
def test_get_style_for_work_item_status(status_name, expected_result):
    result = get_style_for_work_item_status(status_name)
    assert result == expected_result


@pytest.mark.parametrize(
    'status_name, expected_result',
    [
        ('bug', 'red'),
        ('epic', 'yellow'),
        ('task', 'blue'),
        ('other', ''),
    ],
)
def test_get_style_for_work_item_type(status_name, expected_result):
    result = get_style_for_work_item_type(status_name)
    assert result == expected_result
