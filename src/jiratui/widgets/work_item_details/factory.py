from enum import Enum
from typing import Any

from dateutil.parser import isoparse  # type:ignore[import-untyped]
from textual.widget import Widget
from textual.widgets import Select

from jiratui.models import JiraIssue
from jiratui.widgets.work_item_details.fields import (
    WorkItemDynamicFieldUpdateDateTimeWidget,
    WorkItemDynamicFieldUpdateDateWidget,
    WorkItemDynamicFieldUpdateLabelsWidget,
    WorkItemDynamicFieldUpdateMultiCheckboxesWidget,
    WorkItemDynamicFieldUpdateNumericWidget,
    WorkItemDynamicFieldUpdateSelectionWidget,
    WorkItemDynamicFieldUpdateTextWidget,
    WorkItemDynamicFieldUpdateURLWidget,
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
    COMPONENTS = 'components'


class WorkItemManualUpdateFieldNames(Enum):
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
    COMPONENTS = 'components'


class WorkItemUnsupportedUpdateFieldKeys(Enum):
    """The app does not currently support updating the fields with these keys."""

    REPORTER = 'reporter'
    PROJECT = 'project'
    ISSUE_TYPE = 'issuetype'
    DESCRIPTION = 'description'
    SPRINT = 'sprint'
    TEAM = 'team'
    ENVIRONMENT = 'environment'


class WorkItemSupportedCustomFieldSchemas(Enum):
    """The types of custom fields for which the app supports updates."""

    URL = 'com.atlassian.jira.plugin.system.customfieldtypes:url'
    MULTI_CHECKBOXES = 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes'
    FLOAT = 'com.atlassian.jira.plugin.system.customfieldtypes:float'
    SELECT = 'com.atlassian.jira.plugin.system.customfieldtypes:select'
    DATETIME = 'com.atlassian.jira.plugin.system.customfieldtypes:datetime'
    TEXT_FIELD = 'com.atlassian.jira.plugin.system.customfieldtypes:textfield'
    DATE_PICKER = 'com.atlassian.jira.plugin.system.customfieldtypes:datepicker'
    LABELS = 'com.atlassian.jira.plugin.system.customfieldtypes:labels'


def create_dynamic_widgets_for_updating_work_item(
    work_item: JiraIssue,
    skip_fields_ids_or_keys: list[str] | None = None,
) -> list[Widget]:
    """Generates a list of widgets to support updating (some) fields of a work item based on the issue's edit metadata
    and the current values.

    Args:
        work_item: the work item details.
        skip_fields_ids_or_keys: a list of field names or keys to ignore.

    Returns:
        A list of `textual.widget.Widget` instances to support updating fields.
    """

    if not work_item.edit_meta:
        return []

    field_ids_or_keys_to_skip: list[str]
    if skip_fields_ids_or_keys is None:
        field_ids_or_keys_to_skip = []
    else:
        field_ids_or_keys_to_skip = [item.lower() for item in skip_fields_ids_or_keys]

    widgets: list[Widget] = []

    for __field_id, field in work_item.edit_meta.get('fields', {}).items():
        field_name = field.get('name', '')
        # ignore fields that are updated via the static update form
        if field.get('key', '').lower() in [x.value for x in WorkItemManualUpdateFieldKeys]:
            continue

        if field.get('name', '').lower() in [x.value for x in WorkItemManualUpdateFieldNames]:
            continue

        # ignore fields whose update is not supported
        if field.get('key', '').lower() in [x.value for x in WorkItemUnsupportedUpdateFieldKeys]:
            continue

        # ignore the field as requested by the app configuration
        if (
            field_name.lower() in field_ids_or_keys_to_skip
            or field.get('key').lower() in field_ids_or_keys_to_skip
        ):
            continue

        if not (schema := field.get('schema')):
            continue

        # exclude custom fields whose schema is not one of the schemas supported by the app
        if schema_custom_type := schema.get('custom'):
            if schema_custom_type.lower() not in [
                custom_type.value for custom_type in WorkItemSupportedCustomFieldSchemas
            ]:
                continue

        # exclude fields by type; fields of type array allow multiple values at the same time. This requires special
        # treatment via a custom widget to make it easier/nicer in the UI
        # if schema.get('type', '') == 'array':
        #     continue

        widget: Widget | None = None

        # determine if the widget's value can be updated based on the operations supported by the field
        operations = field.get('operations', [])
        field_supports_update = (
            'set' in operations
            or 'add' in operations
            or 'edit' in operations
            or 'remove' in operations
        )

        value: Any
        if schema_custom_type:
            # process custom fields based on the schema custom type
            if schema_custom_type == WorkItemSupportedCustomFieldSchemas.FLOAT.value:
                if field.get('key') in work_item.get_custom_fields():
                    # get the current value of the field from the issue's custom field data
                    if (value := work_item.get_custom_field_value(field.get('key'))) is not None:
                        value = str(value)
                    widget = WorkItemDynamicFieldUpdateNumericWidget(
                        jira_field_key=field.get('key'),
                        value=value,
                        field_supports_update=field_supports_update,
                        original_value=value,
                    )
            elif schema_custom_type == WorkItemSupportedCustomFieldSchemas.DATE_PICKER.value:
                if field.get('key') in work_item.get_custom_fields():
                    # get the current value of the field from the issue's custom field data
                    value = work_item.get_custom_field_value(field.get('key'))
                    widget = WorkItemDynamicFieldUpdateDateWidget(
                        jira_field_key=field.get('key'),
                        value=value if value is not None else '',
                        field_supports_update=field_supports_update,
                        original_value=value if value is not None else '',
                    )
                    if field.get('required'):
                        widget.valid_empty = False
            elif schema_custom_type == WorkItemSupportedCustomFieldSchemas.DATETIME.value:
                if field.get('key') in work_item.get_custom_fields():
                    # get the current value of the field from the issue's custom field data
                    if value := work_item.get_custom_field_value(field.get('key')):
                        value = isoparse(value).strftime('%Y-%m-%d %H:%M:%S')
                    widget = WorkItemDynamicFieldUpdateDateTimeWidget(
                        jira_field_key=field.get('key'),
                        value=value if value is not None else '',
                        field_supports_update=field_supports_update,
                        original_value=value if value is not None else '',
                    )
                    if field.get('required'):
                        widget.valid_empty = False

            elif schema_custom_type == WorkItemSupportedCustomFieldSchemas.SELECT.value:
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
                        jira_field_key=field.get('key'),
                        allow_blank=not field.get('required'),
                        prompt=f'Select {field.get("name")}',
                        field_supports_update=field_supports_update,
                        original_value=value.get('id') if value is not None else None,
                    )
            elif schema_custom_type == WorkItemSupportedCustomFieldSchemas.URL.value:
                if field.get('key') in work_item.get_custom_fields():
                    # get the current value of the field
                    if (value := work_item.get_custom_field_value(field.get('key'))) is None:
                        value = ''
                    widget = WorkItemDynamicFieldUpdateURLWidget(
                        jira_field_key=field.get('key'),
                        value=value,
                        field_supports_update=field_supports_update,
                        original_value=value,
                    )
            elif schema_custom_type == WorkItemSupportedCustomFieldSchemas.MULTI_CHECKBOXES.value:
                # get the current value of the field
                if (value := work_item.get_custom_field_value(field.get('key'))) is None:
                    value = []
                widget = WorkItemDynamicFieldUpdateMultiCheckboxesWidget(
                    jira_field_key=field.get('key'),
                    field_title=field.get('name'),
                    field_supports_update=field_supports_update,
                    allowed_values=field.get('allowedValues', []),
                    current_value=value,
                    original_value=value,
                )
            elif schema_custom_type == WorkItemSupportedCustomFieldSchemas.TEXT_FIELD.value:
                if field.get('key') in work_item.get_custom_fields():
                    # get the current value of the field from the issue's custom field data
                    value = work_item.get_custom_field_value(field.get('key'))
                    widget = WorkItemDynamicFieldUpdateTextWidget(
                        jira_field_key=field.get('key'),
                        value=value or '',
                        field_supports_update=field_supports_update,
                        original_value=value or '',
                    )
            elif schema_custom_type == WorkItemSupportedCustomFieldSchemas.LABELS.value:
                # get the current value of the field
                if (value := work_item.get_custom_field_value(field.get('key'))) is None:
                    value = []
                widget = WorkItemDynamicFieldUpdateLabelsWidget(
                    jira_field_key=field.get('key'),
                    field_supports_update=field_supports_update,
                    value=','.join(value),
                    original_value=value,
                )
        else:
            # process the non-custom fields based on the schema type
            if schema.get('type', '').lower() == 'number':
                if field.get('key') in work_item.get_additional_fields():
                    # get the current value of the field from the issue's additional fields
                    if (
                        value := work_item.get_additional_field_value(field.get('key'))
                    ) is not None:
                        value = str(value)
                    widget = WorkItemDynamicFieldUpdateNumericWidget(
                        jira_field_key=field.get('key'),
                        value=value,
                        field_supports_update=field_supports_update,
                        original_value=value,
                    )
            elif schema.get('type', '').lower() == 'date':
                if field.get('key') in work_item.get_additional_fields():
                    # get the current value of the field from the issue's custom field data
                    value = work_item.get_additional_field_value(field.get('key'))
                    widget = WorkItemDynamicFieldUpdateDateWidget(
                        jira_field_key=field.get('key'),
                        value=value if value is not None else '',
                        field_supports_update=field_supports_update,
                        original_value=value if value is not None else '',
                    )
                    if field.get('required'):
                        widget.valid_empty = False

        if widget:
            widget.border_title = field.get('name').title()
            widget.tooltip = (
                f'{widget.border_title} (Tip: to ignore use the field key: {field.get("key")})'
            )
            if field.get('required'):
                widget.add_class('required')
                widget.border_subtitle = '(*)'

            widgets.append(widget)
    return widgets
