import pytest

from jiratui.app import JiraApp
from jiratui.models import IssueStatus, IssueType, JiraIssue
from jiratui.widgets.common.widgets import (
    DateInputWidget,
    DateTimeInputWidget,
    LabelsWidget,
    MultiSelectWidget,
    NumericInputWidget,
    SelectionWidget,
    TextInputWidget,
    URLWidget,
)
from jiratui.widgets.work_item_details.factory import create_dynamic_widgets_for_updating_work_item


@pytest.fixture
def work_item() -> JiraIssue:
    return JiraIssue(
        id='1',
        key='key-1',
        summary='abcd',
        status=IssueStatus(name='Done', id='1'),
        issue_type=IssueType(id='1', name='Task'),
        edit_meta={
            'fields': {
                'customfield_10021': {
                    'required': False,
                    'schema': {
                        'type': 'number',
                        'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:float',
                        'customId': 10021,
                    },
                    'name': 'Test Field 1',
                    'key': 'customfield_10021',
                    'operations': ['add', 'set', 'remove'],
                    'allowedValues': None,
                },
            }
        },
        custom_fields={'customfield_10021': 'https://foo.bar'},
    )


@pytest.fixture
def work_item_no_custom_fields() -> JiraIssue:
    return JiraIssue(
        id='1',
        key='key-1',
        summary='abcd',
        status=IssueStatus(name='Done', id='1'),
        issue_type=IssueType(id='1', name='Task'),
        edit_meta={
            'fields': {
                'field_key_1': {
                    'required': False,
                    'schema': {
                        'type': 'number',
                    },
                    'name': 'Test Field 1',
                    'key': 'field_key_1',
                    'operations': ['add', 'set', 'remove'],
                    'allowedValues': None,
                },
            }
        },
        additional_fields={'field_key_1': 1.23},
    )


def test_create_dynamic_widgets_without_edit_metadata(work_item: JiraIssue):
    # GIVEN
    work_item.edit_meta = {}
    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.parametrize(
    'field_key',
    [
        'labels',
        'comment',
        'duedate',
        'issuelinks',
        'attachment',
        'assignee',
        'parent',
        'summary',
        'priority',
        'flagged',
        'timetracking',
    ],
)
def test_create_dynamic_widgets_skip_static_update_fields(field_key: str, work_item: JiraIssue):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['key'] = field_key
    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.parametrize(
    'field_name',
    [
        'Labels',
        'comment',
        'duedate',
        'issuelinks',
        'attachment',
        'assignee',
        'parent',
        'summary',
        'priority',
        'flagged',
        'timetracking',
    ],
)
def test_create_dynamic_widgets_skip_static_update_fields_by_name(
    field_name: str, work_item: JiraIssue
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['name'] = field_name
    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.parametrize(
    'field_key',
    [
        'reporter',
        'project',
        'issuetype',
        'description',
        'sprint',
        'team',
        'environment',
    ],
)
def test_create_dynamic_widgets_skip_unsupported_fields(field_key: str, work_item: JiraIssue):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['key'] = field_key
    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.parametrize(
    'skip_fields',
    [
        ['Field_1', 'field 2'],
    ],
)
def test_create_dynamic_widgets_skip_fields_based_on_configuration(
    skip_fields: list[str], work_item: JiraIssue
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['key'] = 'field_1'
    work_item.edit_meta['fields']['customfield_10021']['name'] = 'Field 2'
    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item, skip_fields)
    # THEN
    assert widgets == []


@pytest.mark.parametrize(
    'schema_custom',
    [
        'com.atlassian.jira.plugin.system.customfieldtypes:textarea',
        'com.atlassian.jira.plugin.some.value',
    ],
)
def test_create_dynamic_widgets_skip_custom_fields_with_unsupported_schemas(
    schema_custom: str, work_item: JiraIssue
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = schema_custom
    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


def test_create_dynamic_widgets_skip_fields_with_missing_schema(work_item: JiraIssue):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema'] = {}
    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


###
# FLOAT
###


def test_create_dynamic_widgets_custom_field_float_without_custom_fields_values(
    work_item: JiraIssue,
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:float'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'number'
    work_item.custom_fields = None

    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_float(work_item: JiraIssue, app: JiraApp):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:float'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'number'
    work_item.custom_fields = {'customfield_10021': 12.34}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], NumericInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == 12.34
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False
        assert widgets[0].id == 'customfield_10021'
        assert widgets[0].get_value_for_update() == 12.34


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_float_without_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:float'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'number'
    work_item.custom_fields = {'customfield_10021': None}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], NumericInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value is None
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_float_changing_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:float'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'number'
    work_item.custom_fields = {'customfield_10021': 12.34}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], NumericInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == 12.34
        widgets[0].value = '9.87'
        assert widgets[0].value_has_changed is True
        assert widgets[0].original_value == 12.34


###
# DATEPICKER
###


def test_create_dynamic_widgets_custom_field_date_picker_without_custom_fields_values(
    work_item: JiraIssue,
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:datepicker'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = None

    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_date_picker(work_item: JiraIssue, app: JiraApp):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:datepicker'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': '2025-12-31'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], DateInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == '2025-12-31'
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False
        assert widgets[0].id == 'customfield_10021'
        assert widgets[0].get_value_for_update() == '2025-12-31'


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_date_picker_without_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:datepicker'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': None}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], DateInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value is None  # New behavior: None instead of empty string
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_date_picker_changing_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:datepicker'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': '2025-12-31'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], DateInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == '2025-12-31'
        widgets[0].value = '2025-12-30'
        assert widgets[0].value_has_changed is True
        assert widgets[0].original_value == '2025-12-31'


###
# DATETIME
###


def test_create_dynamic_widgets_custom_field_date_time_without_custom_fields_values(
    work_item: JiraIssue,
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:datetime'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = None

    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_date_time(work_item: JiraIssue, app: JiraApp):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:datetime'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': '2025-12-31 10:20:30'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], DateTimeInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == '2025-12-31 10:20:30'
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False
        assert widgets[0].id == 'customfield_10021'
        assert widgets[0].get_value_for_update() == '2025-12-31T10:20:30'


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_date_time_without_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:datetime'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': None}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], DateTimeInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value is None  # New behavior: None instead of empty string
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_date_time_changing_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:datetime'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': '2025-12-31 10:20:30'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], DateTimeInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == '2025-12-31 10:20:30'
        widgets[0].value = '2025-12-30 10:20:30'
        assert widgets[0].value_has_changed is True
        assert widgets[0].original_value == '2025-12-31 10:20:30'


###
# URL
###


def test_create_dynamic_widgets_custom_field_url_without_custom_fields_values(work_item: JiraIssue):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:url'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = None

    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_url(work_item: JiraIssue, app: JiraApp):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:url'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': 'https://foo.bar'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], URLWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == 'https://foo.bar'
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False
        assert widgets[0].id == 'customfield_10021'
        assert widgets[0].get_value_for_update() == 'https://foo.bar'


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_url_without_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:url'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': None}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], URLWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == ''  # URLWidget converts None to empty string
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_url_changing_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:url'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': 'https://foo.bar'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], URLWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == 'https://foo.bar'
        widgets[0].value = 'https://foo.bar/1'
        assert widgets[0].value_has_changed is True
        assert widgets[0].original_value == 'https://foo.bar'


###
# TEXTFIELD
###


def test_create_dynamic_widgets_custom_field_textfield_without_custom_fields_values(
    work_item: JiraIssue,
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:textfield'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = None

    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_textfield(work_item: JiraIssue, app: JiraApp):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:textfield'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': 'Some text'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], TextInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == 'Some text'
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False
        assert widgets[0].id == 'customfield_10021'
        assert widgets[0].get_value_for_update() == 'Some text'


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_textfield_without_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:textfield'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': None}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], TextInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == ''  # TextInputWidget converts None to empty string
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_textfield_changing_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:textfield'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': 'Some text'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], TextInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == 'Some text'
        widgets[0].value = 'Some other text'
        assert widgets[0].value_has_changed is True
        assert widgets[0].original_value == 'Some text'


###
# SELECT
###


def test_create_dynamic_widgets_custom_field_select_without_custom_fields_values(
    work_item: JiraIssue,
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:select'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'options'
    work_item.custom_fields = None

    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_select_without_allowed_values(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields'] = {
        'customfield_10128': {
            'required': False,
            'schema': {
                'type': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:select',
                'customId': 10128,
            },
            'name': 'Test Field 5',
            'key': 'customfield_10128',
            'operations': ['set'],
            'allowedValues': [],
        }
    }

    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item)
    # THEN
    assert widgets == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_select(work_item: JiraIssue, app: JiraApp):
    # GIVEN
    work_item.edit_meta['fields'] = {
        'customfield_10128': {
            'required': False,
            'schema': {
                'type': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:select',
                'customId': 10128,
            },
            'name': 'Test Field 5',
            'key': 'customfield_10128',
            'operations': ['set'],
            'allowedValues': [
                {'value': 'Option1', 'id': '10022'},
                {'value': 'Option 2', 'id': '10023', 'color': 'GREY_DARKER'},
            ],
        }
    }
    work_item.custom_fields = {'customfield_10128': {'value': 'Option1', 'id': '10022'}}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], SelectionWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10128']['key']
        assert widgets[0].original_value == '10022'
        assert widgets[0].disabled is False
        assert widgets[0].selection == '10022'  # New behavior: selection is set to original value
        assert widgets[0].id == 'customfield_10128'
        assert widgets[0].get_value_for_update() == {
            'id': '10022'
        }  # New behavior: returns original value


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_select_changing_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields'] = {
        'customfield_10128': {
            'required': False,
            'schema': {
                'type': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:select',
                'customId': 10128,
            },
            'name': 'Test Field 5',
            'key': 'customfield_10128',
            'operations': ['set'],
            'allowedValues': [
                {'value': 'Option1', 'id': '10022'},
                {'value': 'Option 2', 'id': '10023', 'color': 'GREY_DARKER'},
            ],
        }
    }
    work_item.custom_fields = {'customfield_10128': {'value': 'Option1', 'id': '10022'}}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], SelectionWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10128']['key']
        assert widgets[0].original_value == '10022'
        assert widgets[0].disabled is False
        assert widgets[0].selection == '10022'  # New behavior: selection is set to original value
        widgets[0].value = '10023'
        assert widgets[0].value_has_changed is True


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_select_without_changing_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields'] = {
        'customfield_10128': {
            'required': False,
            'schema': {
                'type': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:select',
                'customId': 10128,
            },
            'name': 'Test Field 5',
            'key': 'customfield_10128',
            'operations': ['set'],
            'allowedValues': [
                {'value': 'Option1', 'id': '10022'},
                {'value': 'Option 2', 'id': '10023', 'color': 'GREY_DARKER'},
            ],
        }
    }
    work_item.custom_fields = {'customfield_10128': {'value': 'Option1', 'id': '10022'}}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], SelectionWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10128']['key']
        assert widgets[0].original_value == '10022'
        assert widgets[0].disabled is False
        assert widgets[0].selection == '10022'  # New behavior: selection is set to original value
        widgets[0].value = '10022'
        assert widgets[0].value_has_changed is False  # Setting to same value = no change


###
# LABELS
###


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_labels(work_item: JiraIssue, app: JiraApp):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:labels'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': ['label1', 'label2']}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], LabelsWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == ['label1', 'label2']
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False
        assert widgets[0].id == 'customfield_10021'
        assert widgets[0].get_value_for_update() == ['label1', 'label2']


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_labels_without_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:labels'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': None}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], LabelsWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == []
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_labels_changing_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:labels'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'string'
    work_item.custom_fields = {'customfield_10021': ['label1', 'label2']}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], LabelsWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].original_value == ['label1', 'label2']
        widgets[0].value = 'label1,label3'
        assert widgets[0].value_has_changed is True
        assert widgets[0].original_value == ['label1', 'label2']


###
# MULTI_CHECKBOXES
###


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_multicheckboxes_without_custom_fields_values(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['schema']['custom'] = (
        'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes'
    )
    work_item.edit_meta['fields']['customfield_10021']['schema']['type'] = 'array'
    work_item.custom_fields = None

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], MultiSelectWidget)
        assert widgets[0].get_value_for_update() == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_multicheckboxes_without_allowed_values(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields'] = {
        'customfield_10127': {
            'required': False,
            'schema': {
                'type': 'array',
                'items': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                'customId': 10127,
            },
            'name': 'Test Field 4',
            'key': 'customfield_10127',
            'operations': ['add', 'set', 'remove'],
            'allowedValues': [],
        }
    }

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], MultiSelectWidget)
        assert widgets[0].get_value_for_update() == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_multicheckboxes(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields'] = {
        'customfield_10127': {
            'required': False,
            'schema': {
                'type': 'array',
                'items': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                'customId': 10127,
            },
            'name': 'Test Field 4',
            'key': 'customfield_10127',
            'operations': ['add', 'set', 'remove'],
            'allowedValues': [
                {'value': 'Test Option A', 'id': '10020'},
                {'value': 'Test Option B', 'id': '10021'},
            ],
        }
    }
    work_item.custom_fields = {'customfield_10127': [{'value': 'Test Option A', 'id': '10020'}]}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], MultiSelectWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10127']['key']
        assert widgets[0].disabled is False
        assert widgets[0].get_value_for_update() == [{'id': '10020'}]
        assert widgets[0].id == 'customfield_10127'


@pytest.mark.asyncio
async def test_create_dynamic_widgets_custom_field_multicheckboxes_without_changing_value(
    work_item: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item.edit_meta['fields'] = {
        'customfield_10127': {
            'required': False,
            'schema': {
                'type': 'array',
                'items': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                'customId': 10127,
            },
            'name': 'Test Field 4',
            'key': 'customfield_10127',
            'operations': ['add', 'set', 'remove'],
            'allowedValues': [
                {'value': 'Test Option A', 'id': '10020'},
                {'value': 'Test Option B', 'id': '10021'},
            ],
        }
    }
    work_item.custom_fields = {'customfield_10127': [{'value': 'Test Option A', 'id': '10020'}]}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], MultiSelectWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10127']['key']
        assert widgets[0].get_value_for_update() == [{'id': '10020'}]
        assert widgets[0].value_has_changed is False


@pytest.mark.asyncio
async def test_create_dynamic_widgets(work_item: JiraIssue, app: JiraApp):
    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], NumericInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].border_title == 'Test Field 1'
        assert widgets[0].tooltip == 'Test Field 1 (Tip: to ignore use id: customfield_10021)'
        assert widgets[0].id == 'customfield_10021'


@pytest.mark.asyncio
async def test_create_dynamic_widgets_required_field(work_item: JiraIssue, app: JiraApp):
    # GIVEN
    work_item.edit_meta['fields']['customfield_10021']['required'] = True
    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], NumericInputWidget)
        assert widgets[0].id == work_item.edit_meta['fields']['customfield_10021']['key']
        assert widgets[0].border_title == 'Test Field 1'
        assert widgets[0].tooltip == 'Test Field 1 (Tip: to ignore use id: customfield_10021)'
        assert widgets[0].border_subtitle == '(*)'


###
# Non-custom fields - Schema Type: number
###


def test_create_dynamic_widgets_field_number_without_values(work_item_no_custom_fields: JiraIssue):
    # GIVEN
    work_item_no_custom_fields.additional_fields = None
    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item_no_custom_fields)
    # THEN
    assert widgets == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_field_number(
    work_item_no_custom_fields: JiraIssue, app: JiraApp
):
    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item_no_custom_fields)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], NumericInputWidget)
        assert widgets[0].id == work_item_no_custom_fields.edit_meta['fields']['field_key_1']['key']
        assert widgets[0].original_value == 1.23
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False
        assert widgets[0].id == 'field_key_1'


@pytest.mark.asyncio
async def test_create_dynamic_widgets_field_number_without_value(
    work_item_no_custom_fields: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item_no_custom_fields.additional_fields = {'field_key_1': None}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item_no_custom_fields)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], NumericInputWidget)
        assert widgets[0].id == work_item_no_custom_fields.edit_meta['fields']['field_key_1']['key']
        assert widgets[0].original_value is None
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False


@pytest.mark.asyncio
async def test_create_dynamic_widgets_field_number_changing_value(
    work_item_no_custom_fields: JiraIssue, app: JiraApp
):
    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item_no_custom_fields)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], NumericInputWidget)
        assert widgets[0].id == work_item_no_custom_fields.edit_meta['fields']['field_key_1']['key']
        assert widgets[0].original_value == 1.23
        widgets[0].value = '9.87'
        assert widgets[0].value_has_changed is True
        assert widgets[0].original_value == 1.23


###
# Non-custom fields - Schema Type: date
###


def test_create_dynamic_widgets_field_date_without_additional_fields_values(
    work_item_no_custom_fields: JiraIssue,
):
    # GIVEN
    work_item_no_custom_fields.edit_meta['fields']['field_key_1']['schema']['type'] = 'date'
    work_item_no_custom_fields.additional_fields = None

    # WHEN
    widgets = create_dynamic_widgets_for_updating_work_item(work_item_no_custom_fields)
    # THEN
    assert widgets == []


@pytest.mark.asyncio
async def test_create_dynamic_widgets_field_date(
    work_item_no_custom_fields: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item_no_custom_fields.edit_meta['fields']['field_key_1']['schema']['type'] = 'date'
    work_item_no_custom_fields.additional_fields = {'field_key_1': '2025-12-31'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item_no_custom_fields)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], DateInputWidget)
        assert widgets[0].id == work_item_no_custom_fields.edit_meta['fields']['field_key_1']['key']
        assert widgets[0].original_value == '2025-12-31'
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False
        assert widgets[0].id == 'field_key_1'


@pytest.mark.asyncio
async def test_create_dynamic_widgets_field_date_without_value(
    work_item_no_custom_fields: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item_no_custom_fields.edit_meta['fields']['field_key_1']['schema']['type'] = 'date'
    work_item_no_custom_fields.additional_fields = {'field_key_1': None}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item_no_custom_fields)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], DateInputWidget)
        assert widgets[0].id == work_item_no_custom_fields.edit_meta['fields']['field_key_1']['key']
        assert widgets[0].original_value is None  # New behavior: None instead of empty string
        assert widgets[0].value_has_changed is False
        assert widgets[0].disabled is False


@pytest.mark.asyncio
async def test_create_dynamic_widgets_field_date_changing_value(
    work_item_no_custom_fields: JiraIssue, app: JiraApp
):
    # GIVEN
    work_item_no_custom_fields.edit_meta['fields']['field_key_1']['schema']['type'] = 'date'
    work_item_no_custom_fields.additional_fields = {'field_key_1': '2025-12-31'}

    # WHEN
    async with app.run_test():
        widgets = create_dynamic_widgets_for_updating_work_item(work_item_no_custom_fields)
        # THEN
        assert len(widgets) == 1
        assert isinstance(widgets[0], DateInputWidget)
        assert widgets[0].id == work_item_no_custom_fields.edit_meta['fields']['field_key_1']['key']
        assert widgets[0].original_value == '2025-12-31'
        widgets[0].value = '2025-12-30'
        assert widgets[0].value_has_changed is True
        assert widgets[0].original_value == '2025-12-31'
