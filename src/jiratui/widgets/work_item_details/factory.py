from enum import Enum
from typing import Any

from dateutil.parser import isoparse  # type:ignore[import-untyped]
from textual.widget import Widget

from jiratui.models import JiraIssue
from jiratui.widgets.commons import CustomFieldType, FieldMode
from jiratui.widgets.commons.factory_utils import AllowedValuesParser, FieldMetadata, WidgetBuilder
from jiratui.widgets.commons.widgets import LabelsWidget, MultiSelectWidget, MultiUserPickerWidget


class WorkItemManualUpdateFieldKeys(Enum):
    """These fields are excluded from the dynamic updates because they are already part of the details tab's form or,
    they are updated separately."""

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


class WorkItemManualUpdateFieldNames(Enum):
    """These fields are excluded from the dynamic updates because they are already part of the details tab's form or,
    they are updated separately."""

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
    """The app does not currently support updating the fields with these keys."""

    REPORTER = 'reporter'
    PROJECT = 'project'
    ISSUE_TYPE = 'issuetype'
    DESCRIPTION = 'description'
    SPRINT = 'sprint'
    TEAM = 'team'
    ENVIRONMENT = 'environment'


def create_dynamic_widgets_for_updating_work_item(
    work_item: JiraIssue,
    skip_fields_ids_or_keys: list[str] | None = None,
    ignore_filter_ids: list[str] | None = None,
) -> list[Widget]:
    """Generates a list of widgets to support updating (some) fields of a work item based on the issue's edit metadata
    and the current values.

    This function now uses the unified widget factory from `commons.factory_utils` to create mode-aware widgets.

    Args:
        work_item: the work item details.
        ignore_filter_ids: list of field IDs to ignore/exclude from rendering.
        skip_fields_ids_or_keys: (DEPRECATED) a list of field names or keys to ignore. Use `ignore_filter_ids` instead.

    Returns:
        A list of `textual.widget.Widget` instances to support updating fields.
    """

    # handle deprecated skip_fields_ids_or_keys parameter
    field_ids_or_keys_to_skip: list[str]
    if skip_fields_ids_or_keys is None:
        field_ids_or_keys_to_skip = []
    else:
        field_ids_or_keys_to_skip = [item.lower() for item in skip_fields_ids_or_keys]

    # prepare filters for ignoring fields
    ignore_filter_lowercase: set[str] = set()
    if ignore_filter_ids:
        ignore_filter_lowercase = {item.lower() for item in ignore_filter_ids}

    widgets: list[Widget] = []
    builder = WidgetBuilder()

    # extract the fields from edit metadata (if available)
    edit_meta_fields: dict = work_item.edit_meta.get('fields', {}) if work_item.edit_meta else {}

    for __field_id, field in edit_meta_fields.items():
        field_name = field.get('name', '')
        field_key = field.get('key', '')

        # ignore fields that are updated via the static update form
        if field_key and field_key.lower() in [x.value for x in WorkItemManualUpdateFieldKeys]:
            continue

        if field_name and field_name.lower() in [x.value for x in WorkItemManualUpdateFieldNames]:
            continue

        # ignore fields whose update is not supported
        if field_key and field_key.lower() in [x.value for x in WorkItemUnsupportedUpdateFieldKeys]:
            continue

        # ignore fields as requested by the app configuration (DEPRECATED)
        if __field_id.lower() in field_ids_or_keys_to_skip:
            continue
        if field_name and field_name.lower() in field_ids_or_keys_to_skip:
            continue
        if field_key and field_key.lower() in field_ids_or_keys_to_skip:
            continue
        if field.get('fieldId') and field.get('fieldId').lower() in field_ids_or_keys_to_skip:
            continue

        # ignore fields using new logic
        field_identifiers = {__field_id.lower()}
        if field_name:
            field_identifiers.add(field_name.lower())
        if field_key:
            field_identifiers.add(field_key.lower())
        if field.get('fieldId'):
            field_identifiers.add(field.get('fieldId').lower())

        # ignore mode: skip fields in the ignore list
        if ignore_filter_lowercase and any(
            fid in ignore_filter_lowercase for fid in field_identifiers
        ):
            continue

        if not (schema := field.get('schema')):
            continue

        schema_custom_type = schema.get('custom')
        widget: Widget | None = None
        value: Any

        # parse field metadata using the unified FieldMetadata class
        metadata = FieldMetadata(field)
        metadata.field_id = __field_id  # override with the actual field ID; to ensure we always refer to the field's id

        if schema_custom_type:
            # process custom fields based on the schema custom type
            if schema_custom_type == CustomFieldType.FLOAT.value or schema.get('type') == 'number':
                if __field_id in work_item.get_custom_fields():
                    # get the current value of the field from the issue's custom field data
                    value = work_item.get_custom_field_value(__field_id)
                    widget = builder.build_numeric(
                        mode=FieldMode.UPDATE, metadata=metadata, current_value=value
                    )
            elif schema_custom_type == CustomFieldType.DATE_PICKER.value:
                if __field_id in work_item.get_custom_fields():
                    # get the current value of the field from the issue's custom field data
                    value = work_item.get_custom_field_value(__field_id)
                    widget = builder.build_date(
                        mode=FieldMode.UPDATE, metadata=metadata, current_value=value
                    )
            elif schema_custom_type == CustomFieldType.DATETIME.value:
                if __field_id in work_item.get_custom_fields():
                    # get the current value of the field from the issue's custom field data
                    if value := work_item.get_custom_field_value(__field_id):
                        value = isoparse(value).strftime('%Y-%m-%d %H:%M:%S')
                    widget = builder.build_datetime(
                        mode=FieldMode.UPDATE, metadata=metadata, current_value=value
                    )
            elif schema_custom_type == CustomFieldType.SELECT.value:
                # fields of type option allow a single value from a list of options
                if allowed_values := field.get('allowedValues'):
                    options = AllowedValuesParser.parse_options(allowed_values)
                    # get the current value of the field
                    value = work_item.get_custom_field_value(__field_id)
                    widget = builder.build_selection(
                        mode=FieldMode.UPDATE,
                        metadata=metadata,
                        options=options,
                        current_value=value,
                    )
            elif schema_custom_type == CustomFieldType.URL.value:
                if __field_id in work_item.get_custom_fields():
                    # get the current value of the field
                    if (value := work_item.get_custom_field_value(__field_id)) is None:
                        value = ''
                    widget = builder.build_url(
                        mode=FieldMode.UPDATE,
                        metadata=metadata,
                        current_value=value,
                    )
            elif schema_custom_type == CustomFieldType.MULTI_CHECKBOXES.value:
                # get the current value of the field
                if (value := work_item.get_custom_field_value(field_key)) is None:
                    value = []

                # convert value to list of IDs for multi-select widget
                current_ids = []
                if value:
                    for item in value:
                        if isinstance(item, dict) and 'id' in item:
                            current_ids.append(item['id'])
                        elif hasattr(item, 'id'):
                            current_ids.append(item.id)

                # parse options from allowedValues
                options = AllowedValuesParser.parse_options(field.get('allowedValues', []))
                widget = MultiSelectWidget(
                    mode=FieldMode.UPDATE,
                    field_id=__field_id,
                    jira_field_key=metadata.key,
                    options=options,
                    title=field.get('name'),
                    required=field.get('required', False),
                    original_value=current_ids,
                    field_supports_update=metadata.supports_update,
                )
            elif schema_custom_type == CustomFieldType.TEXT_FIELD.value:
                if __field_id in work_item.get_custom_fields():
                    # get the current value of the field from the issue's custom field data
                    value = work_item.get_custom_field_value(__field_id)
                    widget = builder.build_text(
                        mode=FieldMode.UPDATE, metadata=metadata, current_value=value
                    )
            elif schema_custom_type == CustomFieldType.LABELS.value:
                # get the current value of the field
                if (value := work_item.get_custom_field_value(__field_id)) is None:
                    value = []
                widget = LabelsWidget(
                    mode=FieldMode.UPDATE,
                    field_id=__field_id,
                    jira_field_key=metadata.key,
                    title=field.get('name'),
                    original_value=value,
                    supports_update=metadata.supports_update,
                )
            elif schema_custom_type == CustomFieldType.USER_PICKER.value:
                # get the current value of the field
                current_user = work_item.get_custom_field_value(__field_id)
                widget = builder.build_user_picker(
                    mode=FieldMode.UPDATE, metadata=metadata, current_value=current_user
                )
            elif schema_custom_type == CustomFieldType.MULTI_USER_PICKER.value:
                # get the current value of the field
                if (value := work_item.get_custom_field_value(__field_id)) is None:
                    value = []
                widget = MultiUserPickerWidget(
                    mode=FieldMode.UPDATE,
                    field_id=metadata.field_id,
                    jira_field_key=metadata.key,
                    title=field.get('name'),
                    original_value=[
                        {'id': user.get('accountId'), 'name': user.get('displayName')}
                        for user in value
                    ],
                    field_supports_update=metadata.supports_update,
                )
            elif schema_custom_type == CustomFieldType.MULTI_SELECT.value:
                # Multi-select field - similar to multi-checkboxes but different widget type
                if (value := work_item.get_custom_field_value(field_key)) is None:
                    value = []

                # convert value to list of IDs for multi-select widget
                current_ids = []
                if value:
                    for item in value:
                        if isinstance(item, dict) and 'id' in item:
                            current_ids.append(item['id'])
                        elif hasattr(item, 'id'):
                            current_ids.append(item.id)

                # parse options from allowedValues
                options = AllowedValuesParser.parse_options(field.get('allowedValues', []))
                widget = MultiSelectWidget(
                    mode=FieldMode.UPDATE,
                    field_id=__field_id,
                    jira_field_key=metadata.key,
                    options=options,
                    title=field.get('name'),
                    required=field.get('required', False),
                    original_value=current_ids,
                    field_supports_update=metadata.supports_update,
                )
            elif schema_custom_type == CustomFieldType.TEXTAREA.value:
                # Textarea fields are read-only and not supported for updates; skip creating a widget for this type
                pass
            elif schema_custom_type == CustomFieldType.SD_REQUEST_LANGUAGE.value:
                # service Desk request language picker - treated as a select field
                if __field_id in work_item.get_custom_fields():
                    value = work_item.get_custom_field_value(__field_id)

                    # extract the language code if it's a dict with 'languageCode' key
                    if value and isinstance(value, dict) and 'languageCode' in value:
                        value = value['languageCode']

                    # parse options from allowedValues if available
                    options = AllowedValuesParser.parse_options(field.get('allowedValues', []))
                    widget = builder.build_selection(
                        mode=FieldMode.UPDATE,
                        metadata=metadata,
                        options=options,
                        current_value=value,
                    )
        else:
            # process the non-custom fields based on the schema type
            if schema.get('system', '').lower() == 'labels':
                # get the current value of the field
                if (value := work_item.labels) is None:
                    value = []
                widget = builder.build_labels(
                    mode=FieldMode.UPDATE, metadata=metadata, current_value=value
                )
            elif schema.get('type', '').lower() == 'number':
                if __field_id in work_item.get_additional_fields():
                    # get the current value of the field from the issue's additional fields
                    value = work_item.get_additional_field_value(__field_id)
                    widget = builder.build_numeric(
                        mode=FieldMode.UPDATE, metadata=metadata, current_value=value
                    )
            elif schema.get('type', '').lower() == 'date':
                if __field_id in work_item.get_additional_fields():
                    # get the current value of the field from the issue's custom field data
                    value = work_item.get_additional_field_value(__field_id)
                    widget = builder.build_date(
                        mode=FieldMode.UPDATE, metadata=metadata, current_value=value
                    )
            elif schema.get('type', '').lower() == 'array' and field.get('allowedValues'):
                # Handle non-custom array fields with allowedValues (like components)
                # Use native SelectionList widget for multi-select support
                # Check if field_key is a direct attribute on work_item (like 'components')
                value = None
                if field_key and hasattr(work_item, field_key):
                    value = getattr(work_item, field_key)
                elif __field_id in work_item.get_additional_fields():
                    value = work_item.get_additional_field_value(__field_id)

                # convert value to list of IDs for multi-select widget
                current_ids = []
                if value:
                    for item in value:
                        if isinstance(item, dict) and 'id' in item:
                            current_ids.append(item['id'])
                        elif hasattr(item, 'id'):
                            current_ids.append(item.id)

                # parse options from allowedValues
                options = AllowedValuesParser.parse_options(field.get('allowedValues', []))
                widget = MultiSelectWidget(
                    mode=FieldMode.UPDATE,
                    field_id=__field_id,
                    jira_field_key=metadata.key,
                    options=options,
                    title=field.get('name'),
                    required=field.get('required', False),
                    original_value=current_ids,
                    field_supports_update=metadata.supports_update,
                )

        if widget:
            widget.border_title = field.get('name').title()
            widget.tooltip = f'{widget.border_title} (Tip: to ignore use id: {__field_id})'
            if field.get('required'):
                widget.add_class('required')
                widget.border_subtitle = '(*)'
            widgets.append(widget)

    return widgets
