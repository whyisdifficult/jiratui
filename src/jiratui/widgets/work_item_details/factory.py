from enum import Enum
from typing import Any

from textual.widget import Widget
from textual.widgets import Select

from jiratui.models import JiraIssue
from jiratui.widgets.work_item_details.fields import (
    WorkItemDynamicFieldUpdateDateWidget,
    WorkItemDynamicFieldUpdateNumericWidget,
    WorkItemDynamicFieldUpdateSelectionWidget,
    WorkItemDynamicFieldUpdateTextWidget,
    WorkItemDynamicFieldUpdateWidget,
)


class WorkItemManualUpdateFieldKeys(Enum):
    """These fields are excluded from the dynamic updates because they are already part of the details tab's form or,
    they are updated separately."""

    LABELS = 'labels'
    COMMENT = 'comment'
    DUE_DATE = 'duedate'
    ISSUE_LINKS = 'issuelinks'
    ATTACHMENT = 'attachment'
    ASSIGNEE = 'assignee'
    PARENT = 'parent'
    SUMMARY = 'summary'
    PRIORITY = 'priority'
    FLAGGED = 'flagged'
    TIME_TRACKING = 'timetracking'


class WorkItemUnsupportedUpdateFieldKeys(Enum):
    """These fields do not implement update in the app."""

    REPORTER = 'reporter'
    PROJECT = 'project'
    ISSUE_TYPE = 'issuetype'
    DESCRIPTION = 'description'
    SPRINT = 'sprint'
    TEAM = 'team'
    COMPONENTS = 'components'
    ENVIRONMENT = 'environment'


def create_dynamic_widgets_for_updating_work_item(
    work_item: JiraIssue,
    skip_fields_ids_or_keys: list[str] | None = None,
) -> list[Widget]:
    """Generates a list of widgets to support updating (some) fields of a work item based on the issue's edit metadata
    and the current value.

    Args:
        work_item: the work item details.
        skip_fields_ids_or_keys: a list of field names or keys to ignore.

    Returns:
        A list of `Widget` instances to support updating fields.
    """

    if not work_item.edit_meta:
        return []

    if skip_fields_ids_or_keys:
        skip_fields_ids_or_keys = [item.lower() for item in skip_fields_ids_or_keys]

    widgets: list[Widget] = []

    for _, field in work_item.edit_meta.get('fields', {}).items():
        field_name = field.get('name', '')

        # ignore fields that are updated via the static update form
        if field.get('key', '').lower() in [x.value for x in WorkItemManualUpdateFieldKeys]:
            continue

        # ignore fields whose update is not supported
        if field.get('key', '').lower() in [x.value for x in WorkItemUnsupportedUpdateFieldKeys]:
            continue

        # ignore the field as requested by the app configuration
        if (
            field_name.lower() in skip_fields_ids_or_keys
            or field.get('key').lower() in skip_fields_ids_or_keys
        ):
            continue

        if not (schema := field.get('schema')):
            continue

        # exclude fields by schema
        # fields whose schema is a `textarea` are excluded because they are displayed in the Info tab
        if schema.get('custom') in [
            'com.atlassian.jira.plugin.system.customfieldtypes:textarea',
            'com.pyxis.greenhopper.jira:gh-lexo-rank',
        ]:
            continue

        if schema.get('custom', '').startswith(
            'com.atlassian.jira.plugins.jira-development-integration-plugin:'
        ):
            continue

        # exclude fields by type; fields of type array allow multiple values at the same time. This requires special
        # treatment via a custom widget to make it easier/nicer in the UI
        if schema.get('type', '') == 'array':
            continue

        widget: Widget | None = None

        # determine if the widget's value can be updated based on the operations supported by the field
        operations = field.get('operations', [])
        field_supports_update = (
            'set' in operations
            or 'add' in operations
            or 'edit' in operations
            or 'remove' in operations
        )

        if schema.get('type', '').lower() == 'number':
            value: Any = ''
            # get the current value of the field
            if field.get('key') in work_item.additional_fields:
                if (value := work_item.get_additional_field_value(field.get('key'))) is not None:
                    value = str(value)
            elif field.get('key') in work_item.custom_fields:
                if (value := work_item.get_custom_field_value(field.get('key'))) is not None:
                    value = str(value)
            widget = WorkItemDynamicFieldUpdateNumericWidget(
                id=field.get('key'),
                value=value,
                field_supports_update=field_supports_update,
                original_value=value,
            )
        elif schema.get('type', '').lower() == 'string' or schema.get('type', '').lower() == 'any':
            value = ''
            # get the current value of the field
            if field.get('key') in work_item.additional_fields:
                value = work_item.get_additional_field_value(field.get('key'))
            elif field.get('key') in work_item.custom_fields:
                value = work_item.get_custom_field_value(field.get('key'))
            widget = WorkItemDynamicFieldUpdateTextWidget(
                id=field.get('key'),
                value=value,
                field_supports_update=field_supports_update,
                original_value=value,
            )
        elif schema.get('type', '').lower() in ['date', 'datetime']:
            value = ''
            # get the current value of the field
            if field.get('key') in work_item.additional_fields:
                value = work_item.get_additional_field_value(field.get('key'))
            elif field.get('key') in work_item.custom_fields:
                value = work_item.get_custom_field_value(field.get('key'))
            widget = WorkItemDynamicFieldUpdateDateWidget(
                id=field.get('key'),
                value=value,
                field_supports_update=field_supports_update,
                original_value=value,
            )
        elif schema.get('type', '').lower() == 'option':
            # fields of type option allow a single value from a list of options
            if allowed_values := field.get('allowedValues'):
                options: list[tuple[str, str]] = []
                for value in allowed_values:
                    if not (display_value := value.get('name')):
                        display_value = value.get('value')
                    options.append((display_value, value.get('id')))

                # get the current value of the field
                value = work_item.get_custom_field_value(field.get('key'))

                widget = WorkItemDynamicFieldUpdateSelectionWidget(
                    options=options,
                    value=value.get('id') if value is not None else Select.BLANK,
                    id=field.get('key'),
                    allow_blank=not field.get('required'),
                    prompt=f'Select {field.get("name")}',
                    field_supports_update=field_supports_update,
                    original_value=value.get('id') if value is not None else None,
                )
        else:
            value = ''
            # get the current value of the field
            if field.get('key') in work_item.additional_fields:
                value = work_item.get_additional_field_value(field.get('key'))
            elif field.get('key') in work_item.custom_fields:
                value = work_item.get_custom_field_value(field.get('key'))
            widget = WorkItemDynamicFieldUpdateWidget(
                id=field.get('key'),
                field_supports_update=field_supports_update,
                value=value,
                original_value=value,
            )

        if widget:
            widget.border_title = field.get('name').title()
            widget.tooltip = f'{widget.border_title} (Tip: ignore with: {field.get("key")})'
            if field.get('required'):
                widget.add_class('required')
                widget.valid_empty = False
                widget.border_subtitle = '(*)'

            widgets.append(widget)
    return widgets
