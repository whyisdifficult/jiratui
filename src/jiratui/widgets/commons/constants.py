"""Constants for common widgets."""

from enum import Enum


class CustomFieldType(Enum):
    """Known Jira custom field types that map to specific widgets."""

    USER_PICKER = 'com.atlassian.jira.plugin.system.customfieldtypes:userpicker'
    MULTI_USER_PICKER = 'com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker'
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
    MULTI_VERSION = 'com.atlassian.jira.plugin.system.customfieldtypes:multiversion'
    SD_REQUEST_LANGUAGE = (
        'com.atlassian.servicedesk.servicedesk-lingo-integration-plugin:sd-request-language'
    )
    EPIC_LINK = 'com.pyxis.greenhopper.jira:gh-epic-link'
    SPRINT = 'com.pyxis.greenhopper.jira:gh-sprint'
    TEAM = 'com.atlassian.jira.plugin.system.customfieldtypes:atlassian-team'
    TEAMS_RM_TEAM = 'com.atlassian.teams:rm-teams-custom-field-team'


def is_team_field(schema: dict | None) -> bool:
    """Determines if a field's schema corresponds to an Atlassian Team field.

    Depending on the Jira site, the schema's `custom` key is either `...:atlassian-team` or
    `com.atlassian.teams:rm-teams-custom-field-team`; in both cases the `configuration` includes the `atlassian-team`
    key.

    Args:
        schema: the schema of the field as returned by the create/edit metadata.

    Returns:
        `True` if the field is an Atlassian Team field; `False` otherwise.
    """

    if not schema:
        return False
    if schema.get('custom') in (CustomFieldType.TEAM.value, CustomFieldType.TEAMS_RM_TEAM.value):
        return True
    return bool((schema.get('configuration') or {}).get(CustomFieldType.TEAM.value))
