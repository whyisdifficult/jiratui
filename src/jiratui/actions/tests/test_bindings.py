from jiratui.actions.constants import KEY_BINDINGS_LEGACY, KEY_BINDINGS_STANDARD


def test_standard_action_help():
    assert KEY_BINDINGS_STANDARD.get('help').get('keys') == ['f1']


def test_standard_action_server_info():
    assert KEY_BINDINGS_STANDARD.get('server_info').get('keys') == ['f2']


def test_standard_action_config_info():
    assert KEY_BINDINGS_STANDARD.get('config_info').get('keys') == ['f3']


def test_standard_action_focus_project_filter():
    assert KEY_BINDINGS_STANDARD.get('focus_project_filter').get('keys') == ['alt+p']


def test_standard_action_focus_search_work_item_type_filter():
    assert KEY_BINDINGS_STANDARD.get('focus_search_work_item_type_filter').get('keys') == ['alt+t']


def test_standard_action_focus_search_work_item_status_filter():
    assert KEY_BINDINGS_STANDARD.get('focus_search_work_item_status_filter').get('keys') == [
        'alt+s'
    ]


def test_standard_action_focus_search_assignee_filter():
    assert KEY_BINDINGS_STANDARD.get('focus_search_assignee_filter').get('keys') == ['alt+a']


def test_standard_action_focus_search_work_item_key_filter():
    assert KEY_BINDINGS_STANDARD.get('focus_search_work_item_key_filter').get('keys') == ['alt+k']


def test_standard_action_focus_search_created_from_filter():
    assert KEY_BINDINGS_STANDARD.get('focus_search_created_from_filter').get('keys') == ['alt+c']


def test_standard_action_focus_search_created_until_filter():
    assert KEY_BINDINGS_STANDARD.get('focus_search_created_until_filter').get('keys') == ['alt+u']


def test_standard_action_focus_search_sort_filter():
    assert KEY_BINDINGS_STANDARD.get('focus_search_sort_filter').get('keys') == ['alt+o']


def test_standard_action_focus_search_sprint_filter():
    assert KEY_BINDINGS_STANDARD.get('focus_search_sprint_filter').get('keys') == ['alt+v']


def test_standard_action_focus_search_jql():
    assert KEY_BINDINGS_STANDARD.get('focus_search_jql').get('keys') == ['alt+j']


def test_standard_action_search():
    assert KEY_BINDINGS_STANDARD.get('search').get('keys') == ['/']


def test_standard_action_find_by_text():
    assert KEY_BINDINGS_STANDARD.get('find_by_text').get('keys') == ['ctrl+f']


def test_standard_action_focus_search_results():
    assert KEY_BINDINGS_STANDARD.get('focus_search_results').get('keys') == ['1']


def test_standard_action_focus_work_item_information_tab():
    assert KEY_BINDINGS_STANDARD.get('focus_work_item_information_tab').get('keys') == ['2']


def test_standard_action_focus_work_item_details_tab():
    assert KEY_BINDINGS_STANDARD.get('focus_work_item_details_tab').get('keys') == ['3']


def test_standard_action_focus_work_item_comments_tab():
    assert KEY_BINDINGS_STANDARD.get('focus_work_item_comments_tab').get('keys') == ['4']


def test_standard_action_focus_work_item_related_tab():
    assert KEY_BINDINGS_STANDARD.get('focus_work_item_related_tab').get('keys') == ['5']


def test_standard_action_focus_work_item_attachments_tab():
    assert KEY_BINDINGS_STANDARD.get('focus_work_item_attachments_tab').get('keys') == ['6']


def test_standard_action_focus_work_item_links_tab():
    assert KEY_BINDINGS_STANDARD.get('focus_work_item_links_tab').get('keys') == ['7']


def test_standard_action_focus_work_item_subtasks_tab():
    assert KEY_BINDINGS_STANDARD.get('focus_work_item_subtasks_tab').get('keys') == ['8']


def test_standard_action_create_work_item():
    assert KEY_BINDINGS_STANDARD.get('create_work_item').get('keys') == ['ctrl+n']


def test_standard_action_show_recent_history():
    assert KEY_BINDINGS_STANDARD.get('show_recent_history').get('keys') == ['f4']


def test_standard_action_open_go_to_screen():
    assert KEY_BINDINGS_STANDARD.get('open_go_to_screen').get('keys') == ['f5']


def test_standard_action_copy_issue_key():
    assert KEY_BINDINGS_STANDARD.get('copy_issue_key').get('keys') == ['y']


def test_standard_action_copy_issue_url():
    assert KEY_BINDINGS_STANDARD.get('copy_issue_url').get('keys') == ['ctrl+c']


def test_standard_action_copy_content():
    assert KEY_BINDINGS_STANDARD.get('copy_content').get('keys') == ['c']


def test_standard_action_create_git_branch():
    assert KEY_BINDINGS_STANDARD.get('create_git_branch').get('keys') == ['f6']


def test_standard_action_filter():
    assert KEY_BINDINGS_STANDARD.get('filter').get('keys') == ['f']


def test_standard_action_previous_issues_page():
    assert KEY_BINDINGS_STANDARD.get('previous_issues_page').get('keys') == ['[']


def test_standard_action_next_issues_page():
    assert KEY_BINDINGS_STANDARD.get('next_issues_page').get('keys') == [']']


def test_standard_action_delete_work_item():
    assert KEY_BINDINGS_STANDARD.get('delete_work_item').get('keys') == ['x']


def test_standard_action_select_cursor():
    assert KEY_BINDINGS_STANDARD.get('select_cursor').get('keys') == ['enter']


def test_standard_action_cursor_up():
    assert set(KEY_BINDINGS_STANDARD.get('cursor_up').get('keys')) == {'up', 'k'}


def test_standard_action_cursor_down():
    assert set(KEY_BINDINGS_STANDARD.get('cursor_down').get('keys')) == {'down', 'j'}


def test_standard_action_cursor_right():
    assert set(KEY_BINDINGS_STANDARD.get('cursor_right').get('keys')) == {'right', 'l'}


def test_standard_action_cursor_left():
    assert set(KEY_BINDINGS_STANDARD.get('cursor_left').get('keys')) == {'left', 'h'}


def test_standard_action_page_up():
    assert set(KEY_BINDINGS_STANDARD.get('page_up').get('keys')) == {'ctrl+u'}


def test_standard_action_page_down():
    assert KEY_BINDINGS_STANDARD.get('page_down').get('keys') == ['ctrl+d']


def test_standard_action_scroll_top():
    assert KEY_BINDINGS_STANDARD.get('scroll_top').get('keys') == ['g']


def test_standard_action_scroll_bottom():
    assert KEY_BINDINGS_STANDARD.get('scroll_bottom').get('keys') == ['G']


def test_standard_action_scroll_home():
    assert KEY_BINDINGS_STANDARD.get('scroll_home').get('keys') == ['home']


def test_standard_action_scroll_end():
    assert KEY_BINDINGS_STANDARD.get('scroll_end').get('keys') == ['end']


def test_standard_action_scroll_up():
    assert set(KEY_BINDINGS_STANDARD.get('scroll_up').get('keys')) == {'up', 'k'}


def test_standard_action_scroll_down():
    assert set(KEY_BINDINGS_STANDARD.get('scroll_down').get('keys')) == {'down', 'j'}


def test_standard_action_add_comment():
    assert KEY_BINDINGS_STANDARD.get('add_comment').get('keys') == ['a']


def test_standard_action_delete_comment():
    assert KEY_BINDINGS_STANDARD.get('delete_comment').get('keys') == ['x']


def test_standard_action_link_work_item():
    assert KEY_BINDINGS_STANDARD.get('link_work_item').get('keys') == ['a']


def test_standard_action_view_work_item():
    assert KEY_BINDINGS_STANDARD.get('view_work_item').get('keys') == ['v']


def test_standard_action_unlink_work_item():
    assert KEY_BINDINGS_STANDARD.get('unlink_work_item').get('keys') == ['x']


def test_standard_action_add_remote_link():
    assert KEY_BINDINGS_STANDARD.get('add_remote_link').get('keys') == ['a']


def test_standard_action_delete_remote_link():
    assert KEY_BINDINGS_STANDARD.get('delete_remote_link').get('keys') == ['x']


def test_standard_action_create_work_item_subtask():
    assert KEY_BINDINGS_STANDARD.get('create_work_item_subtask').get('keys') == ['a']


def test_standard_action_edit_content():
    assert KEY_BINDINGS_STANDARD.get('edit_content').get('keys') == ['e']


def test_standard_action_open_text_editor():
    assert KEY_BINDINGS_STANDARD.get('open_text_editor').get('keys') == ['ctrl+e']


def test_standard_action_view_content():
    assert KEY_BINDINGS_STANDARD.get('view_content').get('keys') == ['v']


def test_standard_action_save_content():
    assert KEY_BINDINGS_STANDARD.get('save_content').get('keys') == ['ctrl+s']


def test_standard_action_edit_jql():
    assert KEY_BINDINGS_STANDARD.get('edit_jql').get('keys') == ['ctrl+e']


def test_standard_action_view_worklog():
    assert KEY_BINDINGS_STANDARD.get('view_worklog').get('keys') == ['w']


def test_standard_action_log_work():
    assert KEY_BINDINGS_STANDARD.get('log_work').get('keys') == ['l']


def test_standard_action_delete_worklog():
    assert KEY_BINDINGS_STANDARD.get('delete_worklog').get('keys') == ['x']


def test_standard_action_edit_worklog_entry():
    assert KEY_BINDINGS_STANDARD.get('edit_worklog_entry').get('keys') == ['e']


def test_standard_action_flag_work_item():
    assert KEY_BINDINGS_STANDARD.get('flag_work_item').get('keys') == ['*']


def test_standard_action_open_in_browser():
    assert KEY_BINDINGS_STANDARD.get('open_in_browser').get('keys') == ['o']


def test_standard_action_add_attachment():
    assert KEY_BINDINGS_STANDARD.get('add_attachment').get('keys') == ['a']


def test_standard_action_open_attachment():
    assert KEY_BINDINGS_STANDARD.get('open_attachment').get('keys') == ['o']


def test_standard_action_delete_attachment():
    assert KEY_BINDINGS_STANDARD.get('delete_attachment').get('keys') == ['x']


def test_standard_action_empty_recent_history():
    assert KEY_BINDINGS_STANDARD.get('empty_recent_history').get('keys') == ['x']


def test_legacy_action_help():
    assert set(KEY_BINDINGS_LEGACY.get('help').get('keys')) == {
        'f1',
        'ctrl+question_mark',
        'ctrl+shift+slash',
    }


def test_legacy_action_server_info():
    assert KEY_BINDINGS_LEGACY.get('server_info').get('keys') == ['f2']


def test_legacy_action_config_info():
    assert KEY_BINDINGS_LEGACY.get('config_info').get('keys') == ['f3']


def test_legacy_action_focus_project_filter():
    assert KEY_BINDINGS_LEGACY.get('focus_project_filter').get('keys') == ['p']


def test_legacy_action_focus_search_work_item_type_filter():
    assert KEY_BINDINGS_LEGACY.get('focus_search_work_item_type_filter').get('keys') == ['t']


def test_legacy_action_focus_search_work_item_status_filter():
    assert KEY_BINDINGS_LEGACY.get('focus_search_work_item_status_filter').get('keys') == ['s']


def test_legacy_action_focus_search_assignee_filter():
    assert KEY_BINDINGS_LEGACY.get('focus_search_assignee_filter').get('keys') == ['a']


def test_legacy_action_focus_search_work_item_key_filter():
    assert KEY_BINDINGS_LEGACY.get('focus_search_work_item_key_filter').get('keys') == ['k']


def test_legacy_action_focus_search_created_from_filter():
    assert KEY_BINDINGS_LEGACY.get('focus_search_created_from_filter').get('keys') == ['f']


def test_legacy_action_focus_search_created_until_filter():
    assert KEY_BINDINGS_LEGACY.get('focus_search_created_until_filter').get('keys') == ['u']


def test_legacy_action_focus_search_sort_filter():
    assert KEY_BINDINGS_LEGACY.get('focus_search_sort_filter').get('keys') == ['o']


def test_legacy_action_focus_search_sprint_filter():
    assert KEY_BINDINGS_LEGACY.get('focus_search_sprint_filter').get('keys') == ['v']


def test_legacy_action_focus_search_jql():
    assert KEY_BINDINGS_LEGACY.get('focus_search_jql').get('keys') == ['j']


def test_legacy_action_search():
    assert KEY_BINDINGS_LEGACY.get('search').get('keys') == ['ctrl+r']


def test_legacy_action_find_by_text():
    assert KEY_BINDINGS_LEGACY.get('find_by_text').get('keys') == ['/']


def test_legacy_action_focus_search_results():
    assert KEY_BINDINGS_LEGACY.get('focus_search_results').get('keys') == ['1']


def test_legacy_action_focus_work_item_information_tab():
    assert KEY_BINDINGS_LEGACY.get('focus_work_item_information_tab').get('keys') == ['2']


def test_legacy_action_focus_work_item_details_tab():
    assert KEY_BINDINGS_LEGACY.get('focus_work_item_details_tab').get('keys') == ['3']


def test_legacy_action_focus_work_item_comments_tab():
    assert KEY_BINDINGS_LEGACY.get('focus_work_item_comments_tab').get('keys') == ['4']


def test_legacy_action_focus_work_item_related_tab():
    assert KEY_BINDINGS_LEGACY.get('focus_work_item_related_tab').get('keys') == ['5']


def test_legacy_action_focus_work_item_attachments_tab():
    assert KEY_BINDINGS_LEGACY.get('focus_work_item_attachments_tab').get('keys') == ['6']


def test_legacy_action_focus_work_item_links_tab():
    assert KEY_BINDINGS_LEGACY.get('focus_work_item_links_tab').get('keys') == ['7']


def test_legacy_action_focus_work_item_subtasks_tab():
    assert KEY_BINDINGS_LEGACY.get('focus_work_item_subtasks_tab').get('keys') == ['8']


def test_legacy_action_create_work_item():
    assert KEY_BINDINGS_LEGACY.get('create_work_item').get('keys') == ['ctrl+n']


def test_legacy_action_show_recent_history():
    assert KEY_BINDINGS_LEGACY.get('show_recent_history').get('keys') == ['f7']


def test_legacy_action_copy_issue_key():
    assert KEY_BINDINGS_LEGACY.get('copy_issue_key').get('keys') == ['ctrl+k']


def test_legacy_action_copy_issue_url():
    assert KEY_BINDINGS_LEGACY.get('copy_issue_url').get('keys') == ['ctrl+j']


def test_legacy_action_create_git_branch():
    assert KEY_BINDINGS_LEGACY.get('create_git_branch').get('keys') == ['ctrl+g']


def test_legacy_action_filter():
    assert KEY_BINDINGS_LEGACY.get('filter').get('keys') == ['.']


def test_legacy_action_previous_issues_page():
    assert KEY_BINDINGS_LEGACY.get('previous_issues_page').get('keys') == ['alt+left']


def test_legacy_action_next_issues_page():
    assert KEY_BINDINGS_LEGACY.get('next_issues_page').get('keys') == ['alt+right']


def test_legacy_action_delete_work_item():
    assert KEY_BINDINGS_LEGACY.get('delete_work_item').get('keys') == ['d']


def test_legacy_action_open_go_to_screen():
    assert KEY_BINDINGS_LEGACY.get('open_go_to_screen').get('keys') == ['f6']


def test_legacy_action_select_cursor():
    assert KEY_BINDINGS_LEGACY.get('select_cursor').get('keys') == ['enter']


def test_legacy_action_cursor_up():
    assert KEY_BINDINGS_LEGACY.get('cursor_up').get('keys') == ['up']


def test_legacy_action_cursor_down():
    assert KEY_BINDINGS_LEGACY.get('cursor_down').get('keys') == ['down']


def test_legacy_action_cursor_right():
    assert KEY_BINDINGS_LEGACY.get('cursor_right').get('keys') == ['right']


def test_legacy_action_cursor_left():
    assert KEY_BINDINGS_LEGACY.get('cursor_left').get('keys') == ['left']


def test_legacy_action_page_up():
    assert KEY_BINDINGS_LEGACY.get('page_up').get('keys') == ['pageup']


def test_legacy_action_page_down():
    assert KEY_BINDINGS_LEGACY.get('page_down').get('keys') == ['pagedown']


def test_legacy_action_scroll_top():
    assert KEY_BINDINGS_LEGACY.get('scroll_top').get('keys') == ['ctrl+home']


def test_legacy_action_scroll_bottom():
    assert KEY_BINDINGS_LEGACY.get('scroll_bottom').get('keys') == ['ctrl+end']


def test_legacy_action_scroll_home():
    assert KEY_BINDINGS_LEGACY.get('scroll_home').get('keys') == ['home']


def test_legacy_action_scroll_end():
    assert KEY_BINDINGS_LEGACY.get('scroll_end').get('keys') == ['end']


def test_legacy_action_scroll_up():
    assert KEY_BINDINGS_LEGACY.get('scroll_up').get('keys') == ['up']


def test_legacy_action_scroll_down():
    assert KEY_BINDINGS_LEGACY.get('scroll_down').get('keys') == ['down']


def test_legacy_action_add_comment():
    assert KEY_BINDINGS_LEGACY.get('add_comment').get('keys') == ['n']


def test_legacy_action_delete_comment():
    assert KEY_BINDINGS_LEGACY.get('delete_comment').get('keys') == ['d']


def test_legacy_action_link_work_item():
    assert KEY_BINDINGS_LEGACY.get('link_work_item').get('keys') == ['n']


def test_legacy_action_view_work_item():
    assert KEY_BINDINGS_LEGACY.get('view_work_item').get('keys') == ['v']


def test_legacy_action_unlink_work_item():
    assert KEY_BINDINGS_LEGACY.get('unlink_work_item').get('keys') == ['d']


def test_legacy_action_add_remote_link():
    assert KEY_BINDINGS_LEGACY.get('add_remote_link').get('keys') == ['n']


def test_legacy_action_delete_remote_link():
    assert KEY_BINDINGS_LEGACY.get('delete_remote_link').get('keys') == ['d']


def test_legacy_action_create_work_item_subtask():
    assert KEY_BINDINGS_LEGACY.get('create_work_item_subtask').get('keys') == ['n']


def test_legacy_action_edit_content():
    assert KEY_BINDINGS_LEGACY.get('edit_content').get('keys') == ['ctrl+e']


def test_legacy_action_open_text_editor():
    assert KEY_BINDINGS_LEGACY.get('open_text_editor').get('keys') == ['ctrl+e']


def test_legacy_action_view_worklog():
    assert set(KEY_BINDINGS_LEGACY.get('view_worklog').get('keys')) == {'ctrl+l', 'ctrl+t'}


def test_legacy_action_flag_work_item():
    assert KEY_BINDINGS_LEGACY.get('flag_work_item').get('keys') == ['ctrl+f']


def test_legacy_action_log_work():
    assert KEY_BINDINGS_LEGACY.get('log_work').get('keys') == ['n']


def test_legacy_action_open_in_browser():
    assert KEY_BINDINGS_LEGACY.get('open_in_browser').get('keys') == ['ctrl+o']


def test_legacy_action_delete_worklog():
    assert KEY_BINDINGS_LEGACY.get('delete_worklog').get('keys') == ['d']


def test_legacy_action_edit_worklog_entry():
    assert KEY_BINDINGS_LEGACY.get('edit_worklog_entry').get('keys') == ['ctrl+e']


def test_legacy_action_empty_recent_history():
    assert KEY_BINDINGS_LEGACY.get('empty_recent_history').get('keys') == ['d']


def test_legacy_action_view_content():
    assert KEY_BINDINGS_LEGACY.get('view_content').get('keys') == ['v']


def test_legacy_action_copy_content():
    assert KEY_BINDINGS_LEGACY.get('copy_content').get('keys') == ['c']


def test_legacy_action_save_content():
    assert KEY_BINDINGS_LEGACY.get('save_content').get('keys') == ['ctrl+s']


def test_legacy_action_edit_jql():
    assert KEY_BINDINGS_LEGACY.get('edit_jql').get('keys') == ['ctrl+e']


def test_legacy_action_add_attachment():
    assert set(KEY_BINDINGS_LEGACY.get('add_attachment').get('keys')) == {'ctrl+u', 'n'}


def test_legacy_action_open_attachment():
    assert KEY_BINDINGS_LEGACY.get('open_attachment').get('keys') == ['ctrl+o']


def test_legacy_action_delete_attachment():
    assert KEY_BINDINGS_LEGACY.get('delete_attachment').get('keys') == ['d']
