from jiratui.actions.constants import KEY_BINDINGS_LEGACY, KEY_BINDINGS_STANDARD, SupportedActions


def test_standard_action_help():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.HELP.value).get('keys') == ['f1']


def test_standard_action_server_info():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.SERVER_INFO.value).get('keys') == ['f2']


def test_standard_action_config_info():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.CONFIG_INFO.value).get('keys') == ['f3']


def test_standard_action_focus_project_filter():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_PROJECT_FILTER.value).get('keys') == [
        'alt+p'
    ]


def test_standard_action_focus_search_work_item_type_filter():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_SEARCH_WORK_ITEM_TYPE_FILTER.value).get(
        'keys'
    ) == ['alt+t']


def test_standard_action_focus_search_work_item_status_filter():
    assert KEY_BINDINGS_STANDARD.get(
        SupportedActions.FOCUS_SEARCH_WORK_ITEM_STATUS_FILTER.value
    ).get('keys') == ['alt+s']


def test_standard_action_focus_search_assignee_filter():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_SEARCH_ASSIGNEE_FILTER.value).get(
        'keys'
    ) == ['alt+a']


def test_standard_action_focus_search_work_item_key_filter():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_SEARCH_WORK_ITEM_KEY_FILTER.value).get(
        'keys'
    ) == ['alt+k']


def test_standard_action_focus_search_created_from_filter():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_SEARCH_CREATED_FROM_FILTER.value).get(
        'keys'
    ) == ['alt+c']


def test_standard_action_focus_search_created_until_filter():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_SEARCH_CREATED_UNTIL_FILTER.value).get(
        'keys'
    ) == ['alt+u']


def test_standard_action_focus_search_sort_filter():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_SEARCH_SORT_FILTER.value).get(
        'keys'
    ) == ['alt+o']


def test_standard_action_focus_search_sprint_filter():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_SEARCH_SPRINT_FILTER.value).get(
        'keys'
    ) == ['alt+v']


def test_standard_action_focus_search_jql():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_SEARCH_JQL.value).get('keys') == [
        'alt+j'
    ]


def test_standard_action_search():
    assert set(KEY_BINDINGS_STANDARD.get(SupportedActions.SEARCH.value).get('keys')) == {
        '/',
        'ctrl+r',
    }


def test_standard_action_find_by_text():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FIND_BY_TEXT.value).get('keys') == ['ctrl+f']


def test_standard_action_focus_search_results():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_SEARCH_RESULTS.value).get('keys') == [
        '1'
    ]


def test_standard_action_focus_work_item_information_tab():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_WORK_ITEM_INFORMATION_TAB.value).get(
        'keys'
    ) == ['2']


def test_standard_action_focus_work_item_details_tab():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_WORK_ITEM_DETAILS_TAB.value).get(
        'keys'
    ) == ['3']


def test_standard_action_focus_work_item_comments_tab():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_WORK_ITEM_COMMENTS_TAB.value).get(
        'keys'
    ) == ['4']


def test_standard_action_focus_work_item_related_tab():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_WORK_ITEM_RELATED_TAB.value).get(
        'keys'
    ) == ['5']


def test_standard_action_focus_work_item_attachments_tab():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_WORK_ITEM_ATTACHMENTS_TAB.value).get(
        'keys'
    ) == ['6']


def test_standard_action_focus_work_item_links_tab():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_WORK_ITEM_LINKS_TAB.value).get(
        'keys'
    ) == ['7']


def test_standard_action_focus_work_item_subtasks_tab():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FOCUS_WORK_ITEM_SUBTASKS_TAB.value).get(
        'keys'
    ) == ['8']


def test_standard_action_create_work_item():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.CREATE_WORK_ITEM.value).get('keys') == [
        'ctrl+n'
    ]


def test_standard_action_show_recent_history():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.SHOW_RECENT_HISTORY.value).get('keys') == [
        'f4'
    ]


def test_standard_action_open_go_to_screen():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.OPEN_GO_TO_SCREEN.value).get('keys') == ['f5']


def test_standard_action_copy_issue_key():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.COPY_ISSUE_KEY.value).get('keys') == ['y']


def test_standard_action_copy_issue_url():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.COPY_ISSUE_URL.value).get('keys') == [
        'ctrl+c'
    ]


def test_standard_action_copy_content():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.COPY_CONTENT.value).get('keys') == ['c']


def test_standard_action_create_git_branch():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.CREATE_GIT_BRANCH.value).get('keys') == ['f6']


def test_standard_action_filter():
    assert set(KEY_BINDINGS_STANDARD.get(SupportedActions.FILTER.value).get('keys')) == {'f', '.'}


def test_standard_action_previous_issues_page():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.PREVIOUS_ISSUES_PAGE.value).get('keys') == [
        '['
    ]


def test_standard_action_next_issues_page():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.NEXT_ISSUES_PAGE.value).get('keys') == [']']


def test_standard_action_delete_work_item():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.DELETE_WORK_ITEM.value).get('keys') == ['x']


def test_standard_action_select_cursor():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.SELECT_CURSOR.value).get('keys') == ['enter']


def test_standard_action_cursor_up():
    assert set(KEY_BINDINGS_STANDARD.get(SupportedActions.CURSOR_UP.value).get('keys')) == {
        'up',
        'k',
    }


def test_standard_action_cursor_down():
    assert set(KEY_BINDINGS_STANDARD.get(SupportedActions.CURSOR_DOWN.value).get('keys')) == {
        'down',
        'j',
    }


def test_standard_action_cursor_right():
    assert set(KEY_BINDINGS_STANDARD.get(SupportedActions.CURSOR_RIGHT.value).get('keys')) == {
        'right',
        'l',
    }


def test_standard_action_cursor_left():
    assert set(KEY_BINDINGS_STANDARD.get(SupportedActions.CURSOR_LEFT.value).get('keys')) == {
        'left',
        'h',
    }


def test_standard_action_page_up():
    assert set(KEY_BINDINGS_STANDARD.get(SupportedActions.PAGE_UP.value).get('keys')) == {'ctrl+u'}


def test_standard_action_page_down():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.PAGE_DOWN.value).get('keys') == ['ctrl+d']


def test_standard_action_scroll_top():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.SCROLL_TOP.value).get('keys') == ['g']


def test_standard_action_scroll_bottom():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.SCROLL_BOTTOM.value).get('keys') == ['G']


def test_standard_action_scroll_home():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.SCROLL_HOME.value).get('keys') == ['g']


def test_standard_action_scroll_end():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.SCROLL_END.value).get('keys') == ['G']


def test_standard_action_scroll_up():
    assert set(KEY_BINDINGS_STANDARD.get(SupportedActions.SCROLL_UP.value).get('keys')) == {
        'up',
        'k',
    }


def test_standard_action_scroll_down():
    assert set(KEY_BINDINGS_STANDARD.get(SupportedActions.SCROLL_DOWN.value).get('keys')) == {
        'down',
        'j',
    }


def test_standard_action_add_comment():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.ADD_COMMENT.value).get('keys') == ['a']


def test_standard_action_delete_comment():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.DELETE_COMMENT.value).get('keys') == ['x']


def test_standard_action_link_work_item():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.LINK_WORK_ITEM.value).get('keys') == ['a']


def test_standard_action_view_work_item():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.VIEW_WORK_ITEM.value).get('keys') == ['v']


def test_standard_action_unlink_work_item():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.UNLINK_WORK_ITEM.value).get('keys') == ['x']


def test_standard_action_add_remote_link():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.ADD_REMOTE_LINK.value).get('keys') == ['a']


def test_standard_action_delete_remote_link():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.DELETE_REMOTE_LINK.value).get('keys') == ['x']


def test_standard_action_create_work_item_subtask():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.CREATE_WORK_ITEM_SUBTASK.value).get(
        'keys'
    ) == ['a']


def test_standard_action_edit_content():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.EDIT_CONTENT.value).get('keys') == ['e']


def test_standard_action_open_text_editor():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.OPEN_TEXT_EDITOR.value).get('keys') == [
        'ctrl+e'
    ]


def test_standard_action_view_content():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.VIEW_CONTENT.value).get('keys') == ['v']


def test_standard_action_save_content():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.SAVE_CONTENT.value).get('keys') == ['ctrl+s']


def test_standard_action_edit_jql():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.EDIT_JQL.value).get('keys') == ['ctrl+e']


def test_standard_action_view_worklog():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.VIEW_WORKLOG.value).get('keys') == ['w']


def test_standard_action_log_work():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.LOG_WORK.value).get('keys') == ['l']


def test_standard_action_delete_worklog():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.DELETE_WORKLOG.value).get('keys') == ['x']


def test_standard_action_edit_worklog_entry():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.EDIT_WORKLOG_ENTRY.value).get('keys') == ['e']


def test_standard_action_flag_work_item():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.FLAG_WORK_ITEM.value).get('keys') == ['*']


def test_standard_action_open_in_browser():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.OPEN_IN_BROWSER.value).get('keys') == ['o']


def test_standard_action_add_attachment():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.ADD_ATTACHMENT.value).get('keys') == ['a']


def test_standard_action_open_attachment():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.OPEN_ATTACHMENT.value).get('keys') == ['o']


def test_standard_action_delete_attachment():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.DELETE_ATTACHMENT.value).get('keys') == ['x']


def test_standard_action_empty_recent_history():
    assert KEY_BINDINGS_STANDARD.get(SupportedActions.EMPTY_RECENT_HISTORY.value).get('keys') == [
        'x'
    ]


# Legacy Binding Style


def test_legacy_action_help():
    assert set(KEY_BINDINGS_LEGACY.get(SupportedActions.HELP.value).get('keys')) == {
        'f1',
        'ctrl+question_mark',
        'ctrl+shift+slash',
    }


def test_legacy_action_server_info():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SERVER_INFO.value).get('keys') == ['f2']


def test_legacy_action_config_info():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.CONFIG_INFO.value).get('keys') == ['f3']


def test_legacy_action_focus_project_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_PROJECT_FILTER.value).get('keys') == ['p']


def test_legacy_action_focus_search_work_item_type_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_WORK_ITEM_TYPE_FILTER.value).get(
        'keys'
    ) == ['t']


def test_legacy_action_focus_search_work_item_status_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_WORK_ITEM_STATUS_FILTER.value).get(
        'keys'
    ) == ['s']


def test_legacy_action_focus_search_assignee_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_ASSIGNEE_FILTER.value).get(
        'keys'
    ) == ['a']


def test_legacy_action_focus_search_work_item_key_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_WORK_ITEM_KEY_FILTER.value).get(
        'keys'
    ) == ['k']


def test_legacy_action_focus_search_created_from_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_CREATED_FROM_FILTER.value).get(
        'keys'
    ) == ['f']


def test_legacy_action_focus_search_created_until_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_CREATED_UNTIL_FILTER.value).get(
        'keys'
    ) == ['u']


def test_legacy_action_focus_search_sort_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_SORT_FILTER.value).get('keys') == [
        'o'
    ]


def test_legacy_action_focus_search_sprint_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_SPRINT_FILTER.value).get(
        'keys'
    ) == ['v']


def test_legacy_action_focus_search_jql():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_JQL.value).get('keys') == ['j']


def test_legacy_action_search():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SEARCH.value).get('keys') == ['ctrl+r']


def test_legacy_action_find_by_text():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FIND_BY_TEXT.value).get('keys') == ['/']


def test_legacy_action_focus_search_results():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_SEARCH_RESULTS.value).get('keys') == ['1']


def test_legacy_action_focus_work_item_information_tab():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_WORK_ITEM_INFORMATION_TAB.value).get(
        'keys'
    ) == ['2']


def test_legacy_action_focus_work_item_details_tab():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_WORK_ITEM_DETAILS_TAB.value).get(
        'keys'
    ) == ['3']


def test_legacy_action_focus_work_item_comments_tab():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_WORK_ITEM_COMMENTS_TAB.value).get(
        'keys'
    ) == ['4']


def test_legacy_action_focus_work_item_related_tab():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_WORK_ITEM_RELATED_TAB.value).get(
        'keys'
    ) == ['5']


def test_legacy_action_focus_work_item_attachments_tab():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_WORK_ITEM_ATTACHMENTS_TAB.value).get(
        'keys'
    ) == ['6']


def test_legacy_action_focus_work_item_links_tab():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_WORK_ITEM_LINKS_TAB.value).get(
        'keys'
    ) == ['7']


def test_legacy_action_focus_work_item_subtasks_tab():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FOCUS_WORK_ITEM_SUBTASKS_TAB.value).get(
        'keys'
    ) == ['8']


def test_legacy_action_create_work_item():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.CREATE_WORK_ITEM.value).get('keys') == [
        'ctrl+n'
    ]


def test_legacy_action_show_recent_history():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SHOW_RECENT_HISTORY.value).get('keys') == ['f7']


def test_legacy_action_copy_issue_key():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.COPY_ISSUE_KEY.value).get('keys') == ['ctrl+k']


def test_legacy_action_copy_issue_url():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.COPY_ISSUE_URL.value).get('keys') == ['ctrl+j']


def test_legacy_action_create_git_branch():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.CREATE_GIT_BRANCH.value).get('keys') == [
        'ctrl+g'
    ]


def test_legacy_action_filter():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FILTER.value).get('keys') == ['.']


def test_legacy_action_previous_issues_page():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.PREVIOUS_ISSUES_PAGE.value).get('keys') == [
        'alt+left'
    ]


def test_legacy_action_next_issues_page():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.NEXT_ISSUES_PAGE.value).get('keys') == [
        'alt+right'
    ]


def test_legacy_action_delete_work_item():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.DELETE_WORK_ITEM.value).get('keys') == ['d']


def test_legacy_action_open_go_to_screen():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.OPEN_GO_TO_SCREEN.value).get('keys') == ['f6']


def test_legacy_action_select_cursor():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SELECT_CURSOR.value).get('keys') == ['enter']


def test_legacy_action_cursor_up():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.CURSOR_UP.value).get('keys') == ['up']


def test_legacy_action_cursor_down():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.CURSOR_DOWN.value).get('keys') == ['down']


def test_legacy_action_cursor_right():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.CURSOR_RIGHT.value).get('keys') == ['right']


def test_legacy_action_cursor_left():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.CURSOR_LEFT.value).get('keys') == ['left']


def test_legacy_action_page_up():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.PAGE_UP.value).get('keys') == ['pageup']


def test_legacy_action_page_down():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.PAGE_DOWN.value).get('keys') == ['pagedown']


def test_legacy_action_scroll_top():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SCROLL_TOP.value).get('keys') == ['ctrl+home']


def test_legacy_action_scroll_bottom():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SCROLL_BOTTOM.value).get('keys') == ['ctrl+end']


def test_legacy_action_scroll_home():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SCROLL_HOME.value).get('keys') == ['home']


def test_legacy_action_scroll_end():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SCROLL_END.value).get('keys') == ['end']


def test_legacy_action_scroll_up():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SCROLL_UP.value).get('keys') == ['up']


def test_legacy_action_scroll_down():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SCROLL_DOWN.value).get('keys') == ['down']


def test_legacy_action_add_comment():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.ADD_COMMENT.value).get('keys') == ['n']


def test_legacy_action_delete_comment():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.DELETE_COMMENT.value).get('keys') == ['d']


def test_legacy_action_link_work_item():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.LINK_WORK_ITEM.value).get('keys') == ['n']


def test_legacy_action_view_work_item():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.VIEW_WORK_ITEM.value).get('keys') == ['v']


def test_legacy_action_unlink_work_item():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.UNLINK_WORK_ITEM.value).get('keys') == ['d']


def test_legacy_action_add_remote_link():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.ADD_REMOTE_LINK.value).get('keys') == ['n']


def test_legacy_action_delete_remote_link():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.DELETE_REMOTE_LINK.value).get('keys') == ['d']


def test_legacy_action_create_work_item_subtask():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.CREATE_WORK_ITEM_SUBTASK.value).get('keys') == [
        'n'
    ]


def test_legacy_action_edit_content():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.EDIT_CONTENT.value).get('keys') == ['ctrl+e']


def test_legacy_action_open_text_editor():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.OPEN_TEXT_EDITOR.value).get('keys') == [
        'ctrl+e'
    ]


def test_legacy_action_view_worklog():
    assert set(KEY_BINDINGS_LEGACY.get(SupportedActions.VIEW_WORKLOG.value).get('keys')) == {
        'ctrl+l',
        'ctrl+t',
    }


def test_legacy_action_flag_work_item():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.FLAG_WORK_ITEM.value).get('keys') == ['ctrl+f']


def test_legacy_action_log_work():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.LOG_WORK.value).get('keys') == ['n']


def test_legacy_action_open_in_browser():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.OPEN_IN_BROWSER.value).get('keys') == ['ctrl+o']


def test_legacy_action_delete_worklog():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.DELETE_WORKLOG.value).get('keys') == ['d']


def test_legacy_action_edit_worklog_entry():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.EDIT_WORKLOG_ENTRY.value).get('keys') == [
        'ctrl+e'
    ]


def test_legacy_action_empty_recent_history():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.EMPTY_RECENT_HISTORY.value).get('keys') == ['d']


def test_legacy_action_view_content():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.VIEW_CONTENT.value).get('keys') == ['v']


def test_legacy_action_copy_content():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.COPY_CONTENT.value).get('keys') == ['c']


def test_legacy_action_save_content():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.SAVE_CONTENT.value).get('keys') == ['ctrl+s']


def test_legacy_action_edit_jql():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.EDIT_JQL.value).get('keys') == ['ctrl+e']


def test_legacy_action_add_attachment():
    assert set(KEY_BINDINGS_LEGACY.get(SupportedActions.ADD_ATTACHMENT.value).get('keys')) == {
        'ctrl+u',
        'n',
    }


def test_legacy_action_open_attachment():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.OPEN_ATTACHMENT.value).get('keys') == ['ctrl+o']


def test_legacy_action_delete_attachment():
    assert KEY_BINDINGS_LEGACY.get(SupportedActions.DELETE_ATTACHMENT.value).get('keys') == ['d']
