"""Constants for common widgets."""

from enum import Enum


class CustomFieldType(Enum):
    """Known Jira custom field types that map to specific widgets."""

    USER_PICKER = 'com.atlassian.jira.plugin.system.customfieldtypes:userpicker'
    FLOAT = 'com.atlassian.jira.plugin.system.customfieldtypes:float'
    SELECT = 'com.atlassian.jira.plugin.system.customfieldtypes:select'
    DATE_PICKER = 'com.atlassian.jira.plugin.system.customfieldtypes:datepicker'
    DATETIME = 'com.atlassian.jira.plugin.system.customfieldtypes:datetime'
    TEXT_FIELD = 'com.atlassian.jira.plugin.system.customfieldtypes:textfield'
    TEXTAREA = 'com.atlassian.jira.plugin.system.customfieldtypes:textarea'
    LABELS = 'com.atlassian.jira.plugin.system.customfieldtypes:labels'
    URL = 'com.atlassian.jira.plugin.system.customfieldtypes:url'
    MULTI_CHECKBOXES = 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes'
    MULTI_SELECT = 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect'
    SD_REQUEST_LANGUAGE = (
        'com.atlassian.servicedesk.servicedesk-lingo-integration-plugin:sd-request-language'
    )
