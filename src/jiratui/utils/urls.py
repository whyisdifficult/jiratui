from jiratui.config import CONFIGURATION


def build_external_url_for_issue(key: str) -> str | None:
    if base_url := CONFIGURATION.get().jira_base_url:  # type:ignore[union-attr]
        return f'{base_url}/browse/{key}'
    return f'{CONFIGURATION.get().jira_api_base_url}/browse/{key}'


def build_external_url_for_comment(key: str, comment_id: str) -> str | None:
    if base_url := CONFIGURATION.get().jira_base_url:  # type:ignore[union-attr]
        return f'{base_url}/browse/{key}?focusedCommentId={comment_id}'
    return f'{CONFIGURATION.get().jira_api_base_url}/browse/{key}?focusedCommentId={comment_id}'


def build_external_url_for_work_log(key: str, work_log_id: str) -> str | None:
    if base_url := CONFIGURATION.get().jira_base_url:  # type:ignore[union-attr]
        return f'{base_url}/browse/{key}?focusedWorklogId={work_log_id}'
    return f'{CONFIGURATION.get().jira_api_base_url}/browse/{key}?focusedWorklogId={work_log_id}'
