from typing import Any

from textual.widget import Widget
from textual.widgets import Select

from jiratui.api_controller.controller import APIController
from jiratui.config import CONFIGURATION
from jiratui.widgets.commons import CustomFieldType, FieldMode
from jiratui.widgets.commons.factory_utils import AllowedValuesParser
from jiratui.widgets.commons.widgets import (
    DateInputWidget,
    DateTimeInputWidget,
    EpicLinkWidget,
    LabelsWidget,
    MultiSelectWidget,
    MultiUserPickerWidget,
    NumericInputWidget,
    SelectionWidget,
    SingleUserPickerWidget,
    SprintWidget,
    TextInputWidget,
    URLWidget,
)


def create_widgets_for_work_item_creation(
    data: list[dict], api_controller: APIController | None = None
) -> list[Widget]:
    """Creates a list of Textual widgets for the "form" that allows users to create work items.

    Fields that are statically included in the form, such as `project`, `issuetype`, `reporter`, etc. are ignored by
    this function. As a result this function will not return Textual's Widget instances for them. These fields are
    defined in [CREATE_FORM_DEFAULT_FIELDS](#src.jiratui.widgets.create_work_item.factory.CREATE_FORM_DEFAULT_FIELDS).

    Args:
        data: a list of dictionaries with the create-metadata information for all the fields of a given type of work
        item supported in a project.
        api_controller: an optional APIController instance to make requests to the Jira API; unused, for compatibility.

    Returns:
        A list of `textual.widget.Widget` instances for every supported field.
    """

    widgets: list[Widget] = []
    config = CONFIGURATION.get()
    ignore_list = config.create_additional_fields_ignore_ids or []
    enable_additional = config.enable_creating_additional_fields

    for item in data:
        field_id: str = item.get('fieldId')

        if field_id in CREATE_FORM_DEFAULT_FIELDS_IDS:
            # ignore them because they will be included in the form anyway
            continue

        if field_id in FIELDS_IDS_NOT_SUPPORTED:
            continue

        if not (required := item.get('required', False)):
            if field_id in ignore_list:
                continue
            if not enable_additional and field_id not in CREATE_FORM_OPTIONAL_FIELDS_IDS:
                continue

        widget: Widget | None

        if field_id == 'duedate':
            widget = DateInputWidget(
                mode=FieldMode.CREATE,
                field_id=item.get('fieldId') or '',
                jira_field_key=item.get('fieldId'),
                title='Due Date',
                required=required,
            )
        else:
            schema: dict = item.get('schema', {})
            schema_type = schema.get('type', '')
            custom_type: str | None = schema.get('custom')
            if custom_type in CUSTOM_FIELD_TYPES_NOT_SUPPORTED:
                continue
            if custom_type == CustomFieldType.USER_PICKER.value:
                widget = SingleUserPickerWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    required=required,
                    title=item.get('name'),
                )
            elif custom_type == CustomFieldType.MULTI_USER_PICKER.value:
                widget = MultiUserPickerWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    title=item.get('name'),
                    required=required,
                )
            elif custom_type == CustomFieldType.EPIC_LINK.value:
                widget = EpicLinkWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    title=item.get('name'),
                    required=required,
                )
                widget.tooltip = f'{item.get("name")} (Tip: to ignore use id: {field_id})'
            elif custom_type == CustomFieldType.SPRINT.value:
                widget = SprintWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    title=item.get('name'),
                    required=required,
                )
                widget.tooltip = f'{item.get("name")} (Tip: to ignore use id: {field_id})'
            elif custom_type == CustomFieldType.FLOAT.value or (
                schema_type and schema_type.lower() == 'number'
            ):
                widget = NumericInputWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    required=required,
                    title=item.get('name'),
                )
                widget.border_title = item.get('name')
            elif custom_type == CustomFieldType.LABELS.value or (
                schema_type == 'array' and schema.get('system') == 'labels'
            ):
                widget = LabelsWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    title=item.get('name'),
                    required=required,
                )
            elif custom_type == CustomFieldType.DATE_PICKER.value or (
                schema_type and schema_type.lower() == 'date'
            ):
                widget = DateInputWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    required=required,
                    title=item.get('name'),
                )
                widget.border_title = item.get('name')
            elif custom_type == CustomFieldType.DATETIME.value:
                widget = DateTimeInputWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    required=required,
                    title=item.get('name'),
                )
                widget.border_title = item.get('name')
            elif custom_type == CustomFieldType.URL.value:
                widget = URLWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    required=required,
                    title=item.get('name'),
                )
                widget.border_title = item.get('name')
            elif 'allowedValues' in item:
                # the field supports pre-defined values
                if not (allowed_values := item.get('allowedValues')):
                    # if the field does not have any pre-defined values then the field can not be use for creating a
                    # work item because we don't know the possible allowed values to choose from; Jira admins need to
                    # pre-define the values first
                    continue
                options = AllowedValuesParser.parse_options(allowed_values)
                # check if this is an array field (multi-select)
                schema_type = schema.get('type')
                if schema_type == 'array':
                    multi_initial_value = []
                    has_default = item.get('hasDefaultValue', False)
                    if has_default and (default_value := item.get('defaultValue')):
                        if isinstance(default_value, list):
                            multi_initial_value = [
                                str(v.get('id')) for v in default_value if isinstance(v, dict)
                            ]
                        elif isinstance(default_value, dict):
                            multi_initial_value = [str(default_value.get('id'))]

                    widget = MultiSelectWidget(
                        mode=FieldMode.CREATE,
                        field_id=item.get('fieldId') or '',
                        jira_field_key=item.get('key') or field_id,
                        options=options,
                        title=item.get('name'),
                        required=bool(required),
                        initial_value=multi_initial_value,
                        field_supports_update=True,
                    )
                else:
                    allow_blank = True
                    initial_value: Any = Select.NULL
                    has_default = item.get('hasDefaultValue', False)
                    if has_default and (default_value := item.get('defaultValue')):
                        allow_blank = False
                        initial_value = default_value.get('id')

                    widget = SelectionWidget(
                        mode=FieldMode.CREATE,
                        field_id=item.get('fieldId') or '',
                        jira_field_key=item.get('key') or field_id,
                        options=options,
                        title=item.get('name'),
                        required=bool(required),
                        initial_value=initial_value,
                        allow_blank=allow_blank
                        or (initial_value == Select.NULL or not initial_value),
                        prompt=f'Select {item.get("name")}',
                    )
            else:
                # the default widget for any other field
                widget = TextInputWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    jira_field_key=item.get('key') or field_id,
                    title=item.get('name'),
                    required=required,
                    placeholder=f'Enter value for {item.get("name")}...',
                )
                widget.border_title = item.get('name')
                widget.tooltip = f'{item.get("name")} (Tip: to ignore use id: {field_id})'

        if widget is not None:
            # add tooltip for custom fields to help with ignore configuration
            if field_id and field_id.startswith('customfield'):
                field_name = item.get('name', field_id)
                widget.tooltip = f'{field_name} (Tip: to ignore use id: {field_id})'
            widgets.append(widget)
    return widgets


# these custom field types are temporarily not supported because we need special treatment for generating their
# widgets. This requires fetching the list of options, e.g. via autocomplete, and a widget that allows the user to
# select multiple options. I decided to use this approach to exclude them instead of letting the user exclude them via
# # their personal configuration. Otherwise, these fields will be rendered using a default text-based widget and this
# # will cause errors when creating the items; as their values are not simply strings.
FIELDS_IDS_NOT_SUPPORTED = [
    'attachment',
    'issuelinks',
]

# these custom field types are temporarily not supported because we need special treatment for generating their
# widgets. This requires fetching the list of options, e.g. via autocomplete, and a widget that allows the user to
# select multiple options. I decided to use this approach to exclude them instead of letting the user exclude them via
# their personal configuration. Otherwise, these fields will be rendered using a default text-based widget and this
# will cause errors when creating the items; as their values are not simply strings.
CUSTOM_FIELD_TYPES_NOT_SUPPORTED = [
    'com.atlassian.jira.plugin.system.customfieldtypes:atlassian-team',
    'com.pyxis.greenhopper.jira:gh-lexo-rank',  # this requires special syntax
]

CREATE_FORM_DEFAULT_FIELDS_IDS: list[str] = [
    'project',
    'issuetype',
    'reporter',
    'summary',
    'description',
    'parent',
    'assignee',
]
CREATE_FORM_OPTIONAL_FIELDS_IDS: list[str] = [
    'duedate',
    'priority',
]
