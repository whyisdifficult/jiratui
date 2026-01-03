from enum import Enum
from typing import Any

from textual.widget import Widget
from textual.widgets import Select

from jiratui.config import CONFIGURATION
from jiratui.widgets.common.base_fields import FieldMode, UserPickerWidget
from jiratui.widgets.common.factory_utils import (
    AllowedValuesParser,
    CustomFieldType,
)
from jiratui.widgets.common.widgets import (
    DateInputWidget,
    LabelsWidget,
    MultiSelectWidget,
    NumericInputWidget,
    SelectionWidget,
    TextInputWidget,
)


def create_widgets_for_work_item_creation(data: list[dict], api_controller=None) -> list[Widget]:
    """Creates a list of widgets for the "form" that allows users to create work items.

    Args:
        data: a list of dictionaries with the create-metadata information.
        api_controller: Optional API controller instance (unused, for compatibility).

    Returns:
        A list of `textual.widget.Widget` instances for every supported field.
    """

    widgets: list[Widget] = []
    config = CONFIGURATION.get()
    ignore_list = config.create_additional_fields_ignore_ids or []
    enable_additional = config.enable_creating_additional_fields

    for item in data:
        field_id = item.get('fieldId')

        if field_id in SKIP_FIELDS:
            # ignore them because they will be included in the form anyway
            continue

        required = item.get('required', False)

        if not required:
            if field_id in ignore_list:
                continue

            if not enable_additional and field_id not in PROCESS_OPTIONAL_FIELDS:
                continue

        widget: Widget | None = None

        if field_id == CreateWorkItemFieldId.DUE_DATE.value:
            widget = DateInputWidget(
                mode=FieldMode.CREATE,
                field_id=item.get('fieldId') or '',
                title='Due Date',
                required=required,
            )
        else:
            schema = item.get('schema', {})
            custom_type = schema.get('custom')

            if custom_type == CustomFieldType.USER_PICKER.value:
                widget = UserPickerWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    required=required,
                    title=item.get('name'),
                )
            elif custom_type == CustomFieldType.FLOAT.value:
                widget = NumericInputWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    required=required,
                    title=item.get('name'),
                )
            elif custom_type == CustomFieldType.LABELS.value:
                widget = LabelsWidget(
                    mode=FieldMode.CREATE,
                    field_id=field_id or '',
                    title=item.get('name'),
                    required=required,
                )
            elif allowed_values := item.get('allowedValues'):
                options = AllowedValuesParser.parse_options(allowed_values)

                # Check if this is an array field (multi-select)
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
                        options=options,
                        title=item.get('name'),
                        required=bool(required),
                        initial_value=multi_initial_value,
                        field_supports_update=True,
                    )
                else:
                    allow_blank = True
                    initial_value: Any = Select.BLANK
                    has_default = item.get('hasDefaultValue', False)
                    if has_default and (default_value := item.get('defaultValue')):
                        allow_blank = False
                        initial_value = default_value.get('id')

                    widget = SelectionWidget(
                        mode=FieldMode.CREATE,
                        field_id=item.get('fieldId') or '',
                        options=options,
                        title=item.get('name'),
                        required=bool(required),
                        initial_value=initial_value,
                        allow_blank=allow_blank
                        or (initial_value == Select.BLANK or not initial_value),
                        prompt=f'Select {item.get("name")}',
                    )
            else:
                widget = TextInputWidget(
                    mode=FieldMode.CREATE,
                    field_id=item.get('fieldId') or '',
                    title=item.get('name'),
                    required=required,
                    placeholder=f'Enter value for {item.get("name")}...',
                )

        if widget is not None:
            # Add tooltip for custom fields to help with ignore configuration
            if field_id and field_id.startswith('customfield'):
                field_name = item.get('name', field_id)
                widget.tooltip = f'{field_name} (Tip: to ignore use id: {field_id})'
            widgets.append(widget)
    return widgets


class CreateWorkItemFieldId(Enum):
    PROJECT = 'project'
    ISSUE_TYPE = 'issuetype'
    REPORTER = 'reporter'
    SUMMARY = 'summary'
    DESCRIPTION = 'description'
    PARENT = 'parent'
    DUE_DATE = 'duedate'
    PRIORITY = 'priority'


SKIP_FIELDS = [
    CreateWorkItemFieldId.PROJECT.value,
    CreateWorkItemFieldId.ISSUE_TYPE.value,
    CreateWorkItemFieldId.REPORTER.value,
    CreateWorkItemFieldId.SUMMARY.value,
    CreateWorkItemFieldId.DESCRIPTION.value,
    CreateWorkItemFieldId.PARENT.value,
]
PROCESS_OPTIONAL_FIELDS: list[str] = [
    CreateWorkItemFieldId.DUE_DATE.value,
    CreateWorkItemFieldId.PRIORITY.value,
]
