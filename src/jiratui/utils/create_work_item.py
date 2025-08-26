from enum import Enum

from textual.widget import Widget
from textual.widgets import Select

from jiratui.widgets.create_work_item.fields import (
    CreateWorkItemDueDate,
    CreateWorkItemSelectionInput,
    CreateWorkItemTextField,
)


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


def create_widgets_for_work_item_creation(data: list[dict]) -> list[Widget]:
    """Creates a list of widgets for the "form" that allows users to create work items.

    Args:
        data: a list of dictionaries with the create-metadata information.

    Returns:
        A list of `textual.widget.Widget` instances for every supported field.
    """

    widgets: list[Widget] = []
    for item in data:
        field_id = item.get('fieldId')

        if field_id in SKIP_FIELDS:
            # ignore them because they will be included in the form anyway
            continue

        required = item.get('required')
        if not required and (field_id not in PROCESS_OPTIONAL_FIELDS):
            continue

        widget: Widget | None

        if field_id == CreateWorkItemFieldId.DUE_DATE.value:
            widget = CreateWorkItemDueDate(widget_id=item.get('fieldId'), valid_empty=not required)
        else:
            if item.get('allowedValues'):
                options: list[tuple[str, str]] = []
                for value in item.get('allowedValues'):
                    if not (display_value := value.get('name')):
                        display_value = value.get('value')
                    options.append((display_value, value.get('id')))

                allow_blank = True
                initial_value = Select.BLANK
                if item.get('hasDefaultValue') and (default_value := item.get('defaultValue')):
                    allow_blank = False
                    initial_value = default_value.get('id')

                widget = CreateWorkItemSelectionInput(
                    options,
                    id=item.get('fieldId'),
                    allow_blank=allow_blank or (initial_value == Select.BLANK or not initial_value),
                    value=initial_value,
                    prompt=f'Select {item.get("name")}',
                )
                widget.border_title = item.get('name')
            else:
                # we assume this is not a selection-based field and, we treat it as a text-based input
                widget = CreateWorkItemTextField(
                    id=item.get('fieldId'),
                    valid_empty=not required,
                    placeholder=f'Enter value for {item.get("name")}...',
                )
                widget.border_title = item.get('name')
        widgets.append(widget)
    return widgets
