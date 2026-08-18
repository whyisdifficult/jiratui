"""
Important: keep the following points in mind when adding new keybindings:
- A ctrl+h binding is silently dead. `alt+h` works fine. See this for
reference: https://github.com/whyisdifficult/jiratui/pull/327#issuecomment-5251489215
- `alt+f` will not work, similar to `alt+b`, because they are `ctrl+right` and `ctrl+left`, respectively
(not sure why). See this for reference: https://github.com/whyisdifficult/jiratui/pull/327#issuecomment-5253519049
"""

from enum import Enum


class SupportedActions(Enum):
    ADD_ATTACHMENT = 'add_attachment'
    ADD_COMMENT = 'add_comment'
    ADD_REMOTE_LINK = 'add_remote_link'
    CONFIG_INFO = 'config_info'
    COPY_CONTENT = 'copy_content'
    COPY_ISSUE_KEY = 'copy_issue_key'
    COPY_ISSUE_URL = 'copy_issue_url'
    CREATE_GIT_BRANCH = 'create_git_branch'
    CREATE_WORK_ITEM = 'create_work_item'
    CREATE_WORK_ITEM_SUBTASK = 'create_work_item_subtask'
    CURSOR_DOWN = 'cursor_down'
    CURSOR_LEFT = 'cursor_left'
    CURSOR_RIGHT = 'cursor_right'
    CURSOR_UP = 'cursor_up'
    DELETE_ATTACHMENT = 'delete_attachment'
    DELETE_COMMENT = 'delete_comment'
    DELETE_REMOTE_LINK = 'delete_remote_link'
    DELETE_WORKLOG = 'delete_worklog'
    DELETE_WORK_ITEM = 'delete_work_item'
    EDIT_CONTENT = 'edit_content'
    EDIT_JQL = 'edit_jql'
    EDIT_WORKLOG_ENTRY = 'edit_worklog_entry'
    EMPTY_RECENT_HISTORY = 'empty_recent_history'
    FILTER = 'filter'
    FIND_BY_TEXT = 'find_by_text'
    FLAG_WORK_ITEM = 'flag_work_item'
    FOCUS_PROJECT_FILTER = 'focus_project_filter'
    FOCUS_SEARCH_ASSIGNEE_FILTER = 'focus_search_assignee_filter'
    FOCUS_SEARCH_CREATED_FROM_FILTER = 'focus_search_created_from_filter'
    FOCUS_SEARCH_CREATED_UNTIL_FILTER = 'focus_search_created_until_filter'
    FOCUS_SEARCH_JQL = 'focus_search_jql'
    FOCUS_SEARCH_RESULTS = 'focus_search_results'
    FOCUS_SEARCH_SORT_FILTER = 'focus_search_sort_filter'
    FOCUS_SEARCH_SPRINT_FILTER = 'focus_search_sprint_filter'
    FOCUS_SEARCH_WORK_ITEM_KEY_FILTER = 'focus_search_work_item_key_filter'
    FOCUS_SEARCH_WORK_ITEM_STATUS_FILTER = 'focus_search_work_item_status_filter'
    FOCUS_SEARCH_WORK_ITEM_TYPE_FILTER = 'focus_search_work_item_type_filter'
    FOCUS_WORK_ITEM_ATTACHMENTS_TAB = 'focus_work_item_attachments_tab'
    FOCUS_WORK_ITEM_COMMENTS_TAB = 'focus_work_item_comments_tab'
    FOCUS_WORK_ITEM_DETAILS_TAB = 'focus_work_item_details_tab'
    FOCUS_WORK_ITEM_INFORMATION_TAB = 'focus_work_item_information_tab'
    FOCUS_WORK_ITEM_LINKS_TAB = 'focus_work_item_links_tab'
    FOCUS_WORK_ITEM_RELATED_TAB = 'focus_work_item_related_tab'
    FOCUS_WORK_ITEM_SUBTASKS_TAB = 'focus_work_item_subtasks_tab'
    HELP = 'help'
    LINK_WORK_ITEM = 'link_work_item'
    LOG_WORK = 'log_work'
    NEXT_ISSUES_PAGE = 'next_issues_page'
    OPEN_ATTACHMENT = 'open_attachment'
    OPEN_GO_TO_SCREEN = 'open_go_to_screen'
    OPEN_IN_BROWSER = 'open_in_browser'
    OPEN_TEXT_EDITOR = 'open_text_editor'
    PAGE_DOWN = 'page_down'
    PAGE_UP = 'page_up'
    PREVIOUS_ISSUES_PAGE = 'previous_issues_page'
    SAVE_CONTENT = 'save_content'
    SCROLL_BOTTOM = 'scroll_bottom'
    SCROLL_DOWN = 'scroll_down'
    SCROLL_END = 'scroll_end'
    SCROLL_HOME = 'scroll_home'
    SCROLL_TOP = 'scroll_top'
    SCROLL_UP = 'scroll_up'
    SEARCH = 'search'
    SELECT_CURSOR = 'select_cursor'
    SERVER_INFO = 'server_info'
    SHOW_RECENT_HISTORY = 'show_recent_history'
    UNLINK_WORK_ITEM = 'unlink_work_item'
    VIEW_CONTENT = 'view_content'
    VIEW_WORKLOG = 'view_worklog'
    VIEW_WORK_ITEM = 'view_work_item'


KEY_BINDINGS_LEGACY = {
    SupportedActions.HELP.value: {
        'keys': ['f1', 'ctrl+question_mark', 'ctrl+shift+slash'],
        'show': True,
        'description': '?',
        'tooltip': 'Open the help',
    },
    SupportedActions.SERVER_INFO.value: {
        'keys': ['f2'],
        'show': True,
        'description': 'Server',
        'tooltip': 'View details of your Jira server',
    },
    SupportedActions.CONFIG_INFO.value: {
        'keys': ['f3'],
        'show': True,
        'description': '\u2699',
        'tooltip': 'View the configuration file',
    },
    SupportedActions.FOCUS_PROJECT_FILTER.value: {
        'keys': ['p'],
        'show': False,
        'description': 'Focuses the project dropdown',
        'tooltip': 'Focuses the project dropdown',
    },
    SupportedActions.FOCUS_SEARCH_WORK_ITEM_TYPE_FILTER.value: {
        'keys': ['t'],
        'show': False,
        'description': 'Focuses the work item types dropdown',
        'tooltip': 'Focuses the work item types dropdown',
    },
    SupportedActions.FOCUS_SEARCH_WORK_ITEM_STATUS_FILTER.value: {
        'keys': ['s'],
        'show': False,
        'description': 'Focuses the work item statuses dropdown',
        'tooltip': 'Focuses the work item statuses dropdown',
    },
    SupportedActions.FOCUS_SEARCH_ASSIGNEE_FILTER.value: {
        'keys': ['a'],
        'show': False,
        'description': 'Focuses the assignee dropdown',
        'tooltip': 'Focuses the assignee dropdown',
    },
    SupportedActions.FOCUS_SEARCH_WORK_ITEM_KEY_FILTER.value: {
        'keys': ['k'],
        'show': False,
        'description': 'Focuses the work item key search input',
        'tooltip': 'Focuses the work item key search input',
    },
    SupportedActions.FOCUS_SEARCH_CREATED_FROM_FILTER.value: {
        'keys': ['f'],
        'show': False,
        'description': 'Focuses the created-from search input',
        'tooltip': 'Focuses the created-from search input',
    },
    SupportedActions.FOCUS_SEARCH_CREATED_UNTIL_FILTER.value: {
        'keys': ['u'],
        'show': False,
        'description': 'Focuses the created-until search input',
        'tooltip': 'Focuses the created-until search input',
    },
    SupportedActions.FOCUS_SEARCH_SORT_FILTER.value: {
        'keys': ['o'],
        'show': False,
        'description': 'Focuses the sorting search input',
        'tooltip': 'Focuses the sorting search input',
    },
    SupportedActions.FOCUS_SEARCH_SPRINT_FILTER.value: {
        'keys': ['v'],
        'show': False,
        'description': 'Focuses the active-sprint search input',
        'tooltip': 'Focuses the active-sprint search input',
    },
    SupportedActions.FOCUS_SEARCH_JQL.value: {
        'keys': ['j'],
        'show': False,
        'description': 'Focuses the JQL search input',
        'tooltip': 'Focuses the JQL search input',
    },
    SupportedActions.SEARCH.value: {
        'keys': ['ctrl+r'],
        'show': True,
        'description': '\uf002',
        'tooltip': 'Search work items',
    },
    SupportedActions.FIND_BY_TEXT.value: {
        'keys': ['/'],
        'show': True,
        'description': 'Full-Text Search',
        'tooltip': 'Perform a full-text search of work items',
    },
    SupportedActions.FOCUS_SEARCH_RESULTS.value: {
        'keys': ['1'],
        'show': False,
        'description': 'Focuses the search results table',
        'tooltip': 'Focuses the search results table',
    },
    SupportedActions.FOCUS_WORK_ITEM_INFORMATION_TAB.value: {
        'keys': ['2'],
        'show': False,
        'description': 'Focuses the work item information tab',
        'tooltip': 'Focuses the work item information tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_DETAILS_TAB.value: {
        'keys': ['3'],
        'show': False,
        'description': 'Focuses the work item details tab',
        'tooltip': 'Focuses the work item details tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_COMMENTS_TAB.value: {
        'keys': ['4'],
        'show': False,
        'description': 'Focuses the work item comments tab',
        'tooltip': 'Focuses the work item comments tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_RELATED_TAB.value: {
        'keys': ['5'],
        'show': False,
        'description': 'Focuses the related work items tab',
        'tooltip': 'Focuses the related work items tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_ATTACHMENTS_TAB.value: {
        'keys': ['6'],
        'show': False,
        'description': 'Focuses the attachments tab',
        'tooltip': 'Focuses the attachments tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_LINKS_TAB.value: {
        'keys': ['7'],
        'show': False,
        'description': 'Focuses the web links tab',
        'tooltip': 'Focuses the web links tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_SUBTASKS_TAB.value: {
        'keys': ['8'],
        'show': False,
        'description': 'Focuses the work item subtasks tab',
        'tooltip': 'Focuses the work item subtasks tab',
    },
    SupportedActions.CREATE_WORK_ITEM.value: {
        'keys': ['ctrl+n'],
        'show': True,
        'description': 'New Item',
        'tooltip': 'Creates a new work item',
    },
    SupportedActions.SHOW_RECENT_HISTORY.value: {
        'keys': ['f7'],
        'show': True,
        'description': 'Recent',
        'tooltip': 'Shows the recent history',
    },
    SupportedActions.COPY_ISSUE_KEY.value: {
        'keys': ['ctrl+k'],
        'show': True,
        'description': '\u2398 Key',
        'tooltip': 'Copy the work item key',
    },
    SupportedActions.COPY_ISSUE_URL.value: {
        'keys': ['ctrl+j'],
        'show': True,
        'description': '\u2398 URL',
        'tooltip': 'Copy the work item URL',
    },
    SupportedActions.CREATE_GIT_BRANCH.value: {
        'keys': ['ctrl+g'],
        'show': True,
        'description': 'Git',
        'tooltip': 'Creates a Git branch for a work item',
    },
    # search results bindings - begin
    SupportedActions.FILTER.value: {
        'keys': ['.'],
        'show': True,
        'description': 'Filter',
        'tooltip': 'Filter work items in the search results table',
    },
    SupportedActions.PREVIOUS_ISSUES_PAGE.value: {
        'keys': ['alt+left'],
        'show': True,
        'description': '\uf060',
        'tooltip': 'Go to the previous page',
    },
    SupportedActions.NEXT_ISSUES_PAGE.value: {
        'keys': ['alt+right'],
        'show': True,
        'description': '\uf061',
        'tooltip': 'Go to the next page',
    },
    SupportedActions.DELETE_WORK_ITEM.value: {
        'keys': ['d'],
        'show': True,
        'description': '[x]',
        'tooltip': 'Deletes a resource',
    },
    SupportedActions.OPEN_GO_TO_SCREEN.value: {
        'keys': ['f6'],
        'show': True,
        'description': 'Related',
        'tooltip': 'View items related to the selected work item',
    },
    # search results bindings - end
    # datatable bindings - begin
    SupportedActions.SELECT_CURSOR.value: {
        'keys': ['enter'],
        'show': False,
        'description': 'Select the item under the cursor',
        'tooltip': 'Select the item under the cursor',
    },
    SupportedActions.CURSOR_UP.value: {
        'keys': ['up'],
        'show': False,
        'description': 'Move up',
        'tooltip': 'Move up',
    },
    SupportedActions.CURSOR_DOWN.value: {
        'keys': ['down'],
        'show': False,
        'description': 'Move down',
        'tooltip': 'Move down',
    },
    SupportedActions.CURSOR_RIGHT.value: {
        'keys': ['right'],
        'show': False,
        'description': 'Move to the right',
        'tooltip': 'Move to the right',
    },
    SupportedActions.CURSOR_LEFT.value: {
        'keys': ['left'],
        'show': False,
        'description': 'Move to the left',
        'tooltip': 'Move to the left',
    },
    SupportedActions.PAGE_UP.value: {
        'keys': ['pageup'],
        'show': False,
        'description': 'Move 1 page up',
        'tooltip': 'Move 1 page up',
    },
    SupportedActions.PAGE_DOWN.value: {
        'keys': ['pagedown'],
        'show': False,
        'description': 'Move 1 page down',
        'tooltip': 'Move 1 page down',
    },
    SupportedActions.SCROLL_TOP.value: {
        'keys': ['ctrl+home'],
        'show': False,
        'tooltip': 'Scroll to the top',
        'description': 'Scroll to the top',
    },
    SupportedActions.SCROLL_BOTTOM.value: {
        'keys': ['ctrl+end'],
        'show': False,
        'description': 'Scroll to the bottom',
        'tooltip': 'Scroll to the bottom',
    },
    SupportedActions.SCROLL_HOME.value: {
        'keys': ['home'],
        'show': False,
        'description': 'Scroll to the beginning',
        'tooltip': 'Scroll to the beginning',
    },
    SupportedActions.SCROLL_END.value: {
        'keys': ['end'],
        'show': False,
        'description': 'Scroll to the end',
        'tooltip': 'Scroll to the end',
    },
    SupportedActions.SCROLL_UP.value: {
        'keys': ['up'],
        'show': False,
        'description': 'Scroll up the page',
        'tooltip': 'Scroll up the page',
    },
    SupportedActions.SCROLL_DOWN.value: {
        'keys': ['down'],
        'show': False,
        'description': 'Scroll down the page',
        'tooltip': 'Scroll down the page',
    },
    # datatable bindings - end
    SupportedActions.ADD_COMMENT.value: {
        'keys': ['n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a comment',
    },
    SupportedActions.DELETE_COMMENT.value: {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a comment',
    },
    SupportedActions.LINK_WORK_ITEM.value: {
        'keys': ['n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Create a link between work items',
    },
    SupportedActions.VIEW_WORK_ITEM.value: {
        'keys': ['v'],
        'show': True,
        'description': 'Quick View',
        'tooltip': 'View details of a work item',
    },
    SupportedActions.UNLINK_WORK_ITEM.value: {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a link between work items',
    },
    SupportedActions.ADD_REMOTE_LINK.value: {
        'keys': ['n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a web link to a work item',
    },
    SupportedActions.DELETE_REMOTE_LINK.value: {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a web link from a work item',
    },
    SupportedActions.CREATE_WORK_ITEM_SUBTASK.value: {
        'keys': ['n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a subtask to a work item',
    },
    SupportedActions.EDIT_CONTENT.value: {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit the (text) content of a resource',
    },
    SupportedActions.OPEN_TEXT_EDITOR.value: {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Open external editor',
    },
    SupportedActions.VIEW_WORKLOG.value: {
        'keys': ['ctrl+l', 'ctrl+t'],
        'show': True,
        'description': '\u231a',
        'tooltip': 'View the worklog of a work item',
    },
    SupportedActions.FLAG_WORK_ITEM.value: {
        'keys': ['ctrl+f'],
        'show': True,
        'description': '\u2605',
        'tooltip': 'Flag a work item',
    },
    SupportedActions.LOG_WORK.value: {
        'keys': ['n'],
        'show': True,
        'description': '[+]',
        'tooltip': 'Log work done for a work item',
    },
    SupportedActions.OPEN_IN_BROWSER.value: {
        'keys': ['ctrl+o'],
        'show': True,
        'description': '\u29c9',
        'tooltip': 'Open resource in the browser',
    },
    SupportedActions.DELETE_WORKLOG.value: {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete worklog entry',
    },
    SupportedActions.EDIT_WORKLOG_ENTRY.value: {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit worklog entry',
    },
    SupportedActions.EMPTY_RECENT_HISTORY.value: {
        'keys': ['d'],
        'show': True,
        'description': 'Empty History',
        'tooltip': 'Empty recent history',
    },
    SupportedActions.VIEW_CONTENT.value: {
        'keys': ['v'],
        'show': True,
        'description': 'View Content',
        'tooltip': 'View the text content of a resource',
    },
    SupportedActions.COPY_CONTENT.value: {
        'keys': ['c'],
        'show': True,
        'description': 'Copy Content',
        'tooltip': 'Copy the text content of a resource',
    },
    SupportedActions.SAVE_CONTENT.value: {
        'keys': ['ctrl+s'],
        'show': True,
        'description': '\uf0c7',
        'tooltip': 'Save the text content of a resource',
    },
    SupportedActions.EDIT_JQL.value: {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit JQL expressions',
    },
    SupportedActions.ADD_ATTACHMENT.value: {
        'keys': ['ctrl+u', 'n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Attach a file to a work item',
    },
    SupportedActions.OPEN_ATTACHMENT.value: {
        'keys': ['ctrl+o'],
        'show': True,
        'description': 'Open',
        'tooltip': 'Open attachment',
    },
    SupportedActions.DELETE_ATTACHMENT.value: {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete attachment',
    },
}

KEY_BINDINGS_STANDARD = {
    # Help and Information
    SupportedActions.HELP.value: {
        'keys': ['f1'],
        'show': True,
        'description': '?',
        'tooltip': 'Open the help',
    },
    SupportedActions.SERVER_INFO.value: {
        'keys': ['f2'],
        'show': True,
        'description': 'Server',
        'tooltip': 'View details of your Jira server',
    },
    SupportedActions.CONFIG_INFO.value: {
        'keys': ['f3'],
        'show': True,
        'description': '\u2699',
        'tooltip': 'View the configuration file',
    },
    # Filter Focus - Alt+Letter (reliably works)
    SupportedActions.FOCUS_PROJECT_FILTER.value: {
        'keys': ['alt+p'],
        'show': False,
        'description': 'Focuses the project dropdown',
        'tooltip': 'Focuses the project dropdown',
    },
    SupportedActions.FOCUS_SEARCH_WORK_ITEM_TYPE_FILTER.value: {
        'keys': ['alt+t'],
        'show': False,
        'description': 'Focuses the work item types dropdown',
        'tooltip': 'Focuses the work item types dropdown',
    },
    SupportedActions.FOCUS_SEARCH_WORK_ITEM_STATUS_FILTER.value: {
        'keys': ['alt+s'],
        'show': False,
        'description': 'Focuses the work item statuses dropdown',
        'tooltip': 'Focuses the work item statuses dropdown',
    },
    SupportedActions.FOCUS_SEARCH_ASSIGNEE_FILTER.value: {
        'keys': ['alt+a'],
        'show': False,
        'description': 'Focuses the assignee dropdown',
        'tooltip': 'Focuses the assignee dropdown',
    },
    SupportedActions.FOCUS_SEARCH_WORK_ITEM_KEY_FILTER.value: {
        'keys': ['alt+k'],
        'show': False,
        'description': 'Focuses the work item key search input',
        'tooltip': 'Focuses the work item key search input',
    },
    SupportedActions.FOCUS_SEARCH_CREATED_FROM_FILTER.value: {
        'keys': ['alt+c'],
        'show': False,
        'description': 'Focuses the created-from search input',
        'tooltip': 'Focuses the created-from search input',
    },
    SupportedActions.FOCUS_SEARCH_CREATED_UNTIL_FILTER.value: {
        'keys': ['alt+u'],
        'show': False,
        'description': 'Focuses the created-until search input',
        'tooltip': 'Focuses the created-until search input',
    },
    SupportedActions.FOCUS_SEARCH_SORT_FILTER.value: {
        'keys': ['alt+o'],
        'show': False,
        'description': 'Focuses the sorting search input',
        'tooltip': 'Focuses the sorting search input',
    },
    SupportedActions.FOCUS_SEARCH_SPRINT_FILTER.value: {
        'keys': ['alt+v'],
        'show': False,
        'description': 'Focuses the active-sprint search input',
        'tooltip': 'Focuses the active-sprint search input',
    },
    SupportedActions.FOCUS_SEARCH_JQL.value: {
        'keys': ['alt+j'],
        'show': False,
        'description': 'Focuses the JQL search input',
        'tooltip': 'Focuses the JQL search input',
    },
    # Search Actions
    SupportedActions.SEARCH.value: {
        'keys': ['/'],
        'show': True,
        'description': '\uf002',
        'tooltip': 'Search work items',
    },
    SupportedActions.FIND_BY_TEXT.value: {
        'keys': ['ctrl+f'],
        'show': True,
        'description': 'Full-Text Search',
        'tooltip': 'Perform a full-text search of work items',
    },
    # Tab Navigation - use numbers (reliable)
    SupportedActions.FOCUS_SEARCH_RESULTS.value: {
        'keys': ['1'],
        'show': False,
        'description': 'Focuses the search results table',
        'tooltip': 'Focuses the search results table',
    },
    SupportedActions.FOCUS_WORK_ITEM_INFORMATION_TAB.value: {
        'keys': ['2'],
        'show': False,
        'description': 'Focuses the work item information tab',
        'tooltip': 'Focuses the work item information tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_DETAILS_TAB.value: {
        'keys': ['3'],
        'show': False,
        'description': 'Focuses the work item details tab',
        'tooltip': 'Focuses the work item details tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_COMMENTS_TAB.value: {
        'keys': ['4'],
        'show': False,
        'description': 'Focuses the work item comments tab',
        'tooltip': 'Focuses the work item comments tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_RELATED_TAB.value: {
        'keys': ['5'],
        'show': False,
        'description': 'Focuses the related work items tab',
        'tooltip': 'Focuses the related work items tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_ATTACHMENTS_TAB.value: {
        'keys': ['6'],
        'show': False,
        'description': 'Focuses the attachments tab',
        'tooltip': 'Focuses the attachments tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_LINKS_TAB.value: {
        'keys': ['7'],
        'show': False,
        'description': 'Focuses the web links tab',
        'tooltip': 'Focuses the web links tab',
    },
    SupportedActions.FOCUS_WORK_ITEM_SUBTASKS_TAB.value: {
        'keys': ['8'],
        'show': False,
        'description': 'Focuses the work item subtasks tab',
        'tooltip': 'Focuses the work item subtasks tab',
    },
    # Item Creation
    SupportedActions.CREATE_WORK_ITEM.value: {
        'keys': ['ctrl+n'],
        'show': True,
        'description': 'New Item',
        'tooltip': 'Creates a new work item',
    },
    # History and Navigation
    SupportedActions.SHOW_RECENT_HISTORY.value: {
        'keys': ['f4'],
        'show': True,
        'description': 'Recent',
        'tooltip': 'Shows the recent history',
    },
    SupportedActions.OPEN_GO_TO_SCREEN.value: {
        'keys': ['f5'],
        'show': True,
        'description': 'Related',
        'tooltip': 'View items related to the currently selected work item',
    },
    # Copy Actions (single letters work)
    SupportedActions.COPY_ISSUE_KEY.value: {
        'keys': ['y'],
        'show': True,
        'description': '\u2398 Key',
        'tooltip': 'Copy the work item key',
    },
    SupportedActions.COPY_ISSUE_URL.value: {
        'keys': ['ctrl+c'],
        'show': True,
        'description': '\u2398 URL',
        'tooltip': 'Copy the work item URL',
    },
    SupportedActions.COPY_CONTENT.value: {
        'keys': ['c'],
        'show': True,
        'description': 'Copy Content',
        'tooltip': 'Copy the text content of a resource',
    },
    # Git
    SupportedActions.CREATE_GIT_BRANCH.value: {
        'keys': ['f6'],
        'show': True,
        'description': 'Git',
        'tooltip': 'Creates a Git branch for a work item',
    },
    # Search Results Actions
    SupportedActions.FILTER.value: {
        'keys': ['f', '.'],
        'show': True,
        'description': 'Filter',
        'tooltip': 'Filter work items in the search results table',
    },
    SupportedActions.PREVIOUS_ISSUES_PAGE.value: {
        'keys': ['['],
        'show': True,
        'description': '\uf060',
        'tooltip': 'Go to the previous page',
    },
    SupportedActions.NEXT_ISSUES_PAGE.value: {
        'keys': [']'],
        'show': True,
        'description': '\uf061',
        'tooltip': 'Go to the next page',
    },
    SupportedActions.DELETE_WORK_ITEM.value: {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Deletes a resource',
    },
    # DataTable Navigation - vim-style (hjkl)
    SupportedActions.SELECT_CURSOR.value: {
        'keys': ['enter'],
        'show': False,
        'description': 'Select the item under the cursor',
        'tooltip': 'Select the item under the cursor',
    },
    SupportedActions.CURSOR_UP.value: {
        'keys': ['up', 'k'],
        'show': False,
        'description': 'Move up',
        'tooltip': 'Move up',
    },
    SupportedActions.CURSOR_DOWN.value: {
        'keys': ['down', 'j'],
        'show': False,
        'description': 'Move down',
        'tooltip': 'Move down',
    },
    SupportedActions.CURSOR_RIGHT.value: {
        'keys': ['right', 'l'],
        'show': False,
        'description': 'Move to the right',
        'tooltip': 'Move to the right',
    },
    SupportedActions.CURSOR_LEFT.value: {
        'keys': ['left', 'h'],
        'show': False,
        'description': 'Move to the left',
        'tooltip': 'Move to the left',
    },
    SupportedActions.PAGE_UP.value: {
        'keys': ['ctrl+u'],
        'show': False,
        'description': 'Move 1 page up',
        'tooltip': 'Move 1 page up',
    },
    SupportedActions.PAGE_DOWN.value: {
        'keys': ['ctrl+d'],
        'show': False,
        'description': 'Move 1 page down',
        'tooltip': 'Move 1 page down',
    },
    SupportedActions.SCROLL_TOP.value: {
        'keys': ['g'],
        'show': False,
        'description': 'Scroll to the top',
        'tooltip': 'Scroll to the top',
    },
    SupportedActions.SCROLL_BOTTOM.value: {
        'keys': ['G'],
        'show': False,
        'description': 'Scroll to the bottom',
        'tooltip': 'Scroll to the bottom',
    },
    SupportedActions.SCROLL_HOME.value: {
        'keys': ['g'],
        'show': False,
        'description': 'Scroll to the beginning',
        'tooltip': 'Scroll to the beginning',
    },
    SupportedActions.SCROLL_END.value: {
        'keys': ['G'],
        'show': False,
        'description': 'Scroll to the end',
        'tooltip': 'Scroll to the end',
    },
    SupportedActions.SCROLL_UP.value: {
        'keys': ['up', 'k'],
        'show': False,
        'description': 'Scroll up the page',
        'tooltip': 'Scroll up the page',
    },
    SupportedActions.SCROLL_DOWN.value: {
        'keys': ['down', 'j'],
        'show': False,
        'description': 'Scroll down the page',
        'tooltip': 'Scroll down the page',
    },
    # Comments
    SupportedActions.ADD_COMMENT.value: {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a comment',
    },
    SupportedActions.DELETE_COMMENT.value: {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a comment',
    },
    # Work Item Links
    SupportedActions.LINK_WORK_ITEM.value: {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Create a link between work items',
    },
    SupportedActions.VIEW_WORK_ITEM.value: {
        'keys': ['v'],
        'show': True,
        'description': '\u2139',
        'tooltip': 'View details of a work item',
    },
    SupportedActions.UNLINK_WORK_ITEM.value: {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a link between work items',
    },
    # Remote Links (Web Links)
    SupportedActions.ADD_REMOTE_LINK.value: {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a web link to a work item',
    },
    SupportedActions.DELETE_REMOTE_LINK.value: {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a web link from a work item',
    },
    # Subtasks
    SupportedActions.CREATE_WORK_ITEM_SUBTASK.value: {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a subtask to a work item',
    },
    # Content Editing
    SupportedActions.EDIT_CONTENT.value: {
        'keys': ['e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit the (text) content of a resource',
    },
    SupportedActions.OPEN_TEXT_EDITOR.value: {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Open text editor',
    },
    SupportedActions.VIEW_CONTENT.value: {
        'keys': ['v'],
        'show': True,
        'description': 'View Content',
        'tooltip': 'View the text content of a resource',
    },
    SupportedActions.SAVE_CONTENT.value: {
        'keys': ['ctrl+s'],
        'show': True,
        'description': '\uf0c7',
        'tooltip': 'Save the text content of a resource',
    },
    SupportedActions.EDIT_JQL.value: {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit JQL expressions',
    },
    # Worklog
    SupportedActions.VIEW_WORKLOG.value: {
        'keys': ['w'],
        'show': True,
        'description': '\u231a',
        'tooltip': 'View the worklog of a work item',
    },
    SupportedActions.LOG_WORK.value: {
        'keys': ['l'],
        'show': True,
        'description': '[+]',
        'tooltip': 'Log work done for a work item',
    },
    SupportedActions.DELETE_WORKLOG.value: {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete worklog entry',
    },
    SupportedActions.EDIT_WORKLOG_ENTRY.value: {
        'keys': ['e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit worklog entry',
    },
    # Flags
    SupportedActions.FLAG_WORK_ITEM.value: {
        'keys': ['*'],
        'show': True,
        'description': '\u2605',
        'tooltip': 'Flag a work item',
    },
    # Browser and Attachments
    SupportedActions.OPEN_IN_BROWSER.value: {
        'keys': ['o'],
        'show': True,
        'description': '\u2197',
        'tooltip': 'Open resource in the browser',
    },
    SupportedActions.ADD_ATTACHMENT.value: {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Attach a file to a work item',
    },
    SupportedActions.OPEN_ATTACHMENT.value: {
        'keys': ['o'],
        'show': True,
        'description': '\u2197',
        'tooltip': 'Open attachment',
    },
    SupportedActions.DELETE_ATTACHMENT.value: {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete attachment',
    },
    # History
    SupportedActions.EMPTY_RECENT_HISTORY.value: {
        'keys': ['x'],
        'show': True,
        'description': 'Empty History',
        'tooltip': 'Empty recent history',
    },
}
