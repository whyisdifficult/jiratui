"""
Important: keep the following points in mind when adding new keybindings:
- A ctrl+h binding is silently dead. `alt+h` works fine. See this for
reference: https://github.com/whyisdifficult/jiratui/pull/327#issuecomment-5251489215
- `alt+f` will not work, similar to `alt+b`, because they are `ctrl+right` and `ctrl+left`, respectively
(not sure why). See this for reference: https://github.com/whyisdifficult/jiratui/pull/327#issuecomment-5253519049
"""

KEY_BINDINGS_LEGACY = {
    'help': {
        'keys': ['f1', 'ctrl+question_mark', 'ctrl+shift+slash'],
        'show': True,
        'description': '?',
        'tooltip': 'Open the help',
    },
    'server_info': {
        'keys': ['f2'],
        'show': True,
        'description': 'Server',
        'tooltip': 'View details of your Jira server',
    },
    'config_info': {
        'keys': ['f3'],
        'show': True,
        'description': '\u2699',
        'tooltip': 'View the configuration file',
    },
    'focus_project_filter': {
        'keys': ['p'],
        'show': False,
        'description': 'Focuses the project dropdown',
        'tooltip': 'Focuses the project dropdown',
    },
    'focus_search_work_item_type_filter': {
        'keys': ['t'],
        'show': False,
        'description': 'Focuses the work item types dropdown',
        'tooltip': 'Focuses the work item types dropdown',
    },
    'focus_search_work_item_status_filter': {
        'keys': ['s'],
        'show': False,
        'description': 'Focuses the work item statuses dropdown',
        'tooltip': 'Focuses the work item statuses dropdown',
    },
    'focus_search_assignee_filter': {
        'keys': ['a'],
        'show': False,
        'description': 'Focuses the assignee dropdown',
        'tooltip': 'Focuses the assignee dropdown',
    },
    'focus_search_work_item_key_filter': {
        'keys': ['k'],
        'show': False,
        'description': 'Focuses the work item key search input',
        'tooltip': 'Focuses the work item key search input',
    },
    'focus_search_created_from_filter': {
        'keys': ['f'],
        'show': False,
        'description': 'Focuses the created-from search input',
        'tooltip': 'Focuses the created-from search input',
    },
    'focus_search_created_until_filter': {
        'keys': ['u'],
        'show': False,
        'description': 'Focuses the created-until search input',
        'tooltip': 'Focuses the created-until search input',
    },
    'focus_search_sort_filter': {
        'keys': ['o'],
        'show': False,
        'description': 'Focuses the sorting search input',
        'tooltip': 'Focuses the sorting search input',
    },
    'focus_search_sprint_filter': {
        'keys': ['v'],
        'show': False,
        'description': 'Focuses the active-sprint search input',
        'tooltip': 'Focuses the active-sprint search input',
    },
    'focus_search_jql': {
        'keys': ['j'],
        'show': False,
        'description': 'Focuses the JQL search input',
        'tooltip': 'Focuses the JQL search input',
    },
    'search': {
        'keys': ['ctrl+r'],
        'show': True,
        'description': '\uf002',
        'tooltip': 'Search work items',
    },
    'find_by_text': {
        'keys': ['/'],
        'show': True,
        'description': 'Full-Text Search',
        'tooltip': 'Perform a full-text search of work items',
    },
    'focus_search_results': {
        'keys': ['1'],
        'show': False,
        'description': 'Focuses the search results table',
        'tooltip': 'Focuses the search results table',
    },
    'focus_work_item_information_tab': {
        'keys': ['2'],
        'show': False,
        'description': 'Focuses the work item information tab',
        'tooltip': 'Focuses the work item information tab',
    },
    'focus_work_item_details_tab': {
        'keys': ['3'],
        'show': False,
        'description': 'Focuses the work item details tab',
        'tooltip': 'Focuses the work item details tab',
    },
    'focus_work_item_comments_tab': {
        'keys': ['4'],
        'show': False,
        'description': 'Focuses the work item comments tab',
        'tooltip': 'Focuses the work item comments tab',
    },
    'focus_work_item_related_tab': {
        'keys': ['5'],
        'show': False,
        'description': 'Focuses the related work items tab',
        'tooltip': 'Focuses the related work items tab',
    },
    'focus_work_item_attachments_tab': {
        'keys': ['6'],
        'show': False,
        'description': 'Focuses the attachments tab',
        'tooltip': 'Focuses the attachments tab',
    },
    'focus_work_item_links_tab': {
        'keys': ['7'],
        'show': False,
        'description': 'Focuses the web links tab',
        'tooltip': 'Focuses the web links tab',
    },
    'focus_work_item_subtasks_tab': {
        'keys': ['8'],
        'show': False,
        'description': 'Focuses the work item subtasks tab',
        'tooltip': 'Focuses the work item subtasks tab',
    },
    'create_work_item': {
        'keys': ['ctrl+n'],
        'show': True,
        'description': 'New Item',
        'tooltip': 'Creates a new work item',
    },
    'show_recent_history': {
        'keys': ['f7'],
        'show': True,
        'description': 'Recent',
        'tooltip': 'Shows the recent history',
    },
    'copy_issue_key': {
        'keys': ['ctrl+k'],
        'show': True,
        'description': '\u2398 Key',
        'tooltip': 'Copy the work item key',
    },
    'copy_issue_url': {
        'keys': ['ctrl+j'],
        'show': True,
        'description': '\u2398 URL',
        'tooltip': 'Copy the work item URL',
    },
    'create_git_branch': {
        'keys': ['ctrl+g'],
        'show': True,
        'description': 'Git',
        'tooltip': 'Creates a Git branch for a work item',
    },
    # search results bindings - begin
    'filter': {
        'keys': ['.'],
        'show': True,
        'description': 'Filter',
        'tooltip': 'Filter work items in the search results table',
    },
    'previous_issues_page': {
        'keys': ['alt+left'],
        'show': True,
        'description': '\uf060',
        'tooltip': 'Go to the previous page',
    },
    'next_issues_page': {
        'keys': ['alt+right'],
        'show': True,
        'description': '\uf061',
        'tooltip': 'Go to the next page',
    },
    'delete_work_item': {
        'keys': ['d'],
        'show': True,
        'description': '[x]',
        'tooltip': 'Deletes a resource',
    },
    'open_go_to_screen': {
        'keys': ['f6'],
        'show': True,
        'description': 'Related',
        'tooltip': 'View items related to the selected work item',
    },
    # search results bindings - end
    # datatable bindings - begin
    'select_cursor': {
        'keys': ['enter'],
        'show': False,
        'description': 'Select the item under the cursor',
        'tooltip': 'Select the item under the cursor',
    },
    'cursor_up': {
        'keys': ['up'],
        'show': False,
        'description': 'Move up',
        'tooltip': 'Move up',
    },
    'cursor_down': {
        'keys': ['down'],
        'show': False,
        'description': 'Move down',
        'tooltip': 'Move down',
    },
    'cursor_right': {
        'keys': ['right'],
        'show': False,
        'description': 'Move to the right',
        'tooltip': 'Move to the right',
    },
    'cursor_left': {
        'keys': ['left'],
        'show': False,
        'description': 'Move to the left',
        'tooltip': 'Move to the left',
    },
    'page_up': {
        'keys': ['pageup'],
        'show': False,
        'description': 'Move 1 page up',
        'tooltip': 'Move 1 page up',
    },
    'page_down': {
        'keys': ['pagedown'],
        'show': False,
        'description': 'Move 1 page down',
        'tooltip': 'Move 1 page down',
    },
    'scroll_top': {
        'keys': ['ctrl+home'],
        'show': False,
        'tooltip': 'Scroll to the top',
        'description': 'Scroll to the top',
    },
    'scroll_bottom': {
        'keys': ['ctrl+end'],
        'show': False,
        'description': 'Scroll to the bottom',
        'tooltip': 'Scroll to the bottom',
    },
    'scroll_home': {
        'keys': ['home'],
        'show': False,
        'description': 'Scroll to the beginning',
        'tooltip': 'Scroll to the beginning',
    },
    'scroll_end': {
        'keys': ['end'],
        'show': False,
        'description': 'Scroll to the end',
        'tooltip': 'Scroll to the end',
    },
    'scroll_up': {
        'keys': ['up'],
        'show': False,
        'description': 'Scroll up the page',
        'tooltip': 'Scroll up the page',
    },
    'scroll_down': {
        'keys': ['down'],
        'show': False,
        'description': 'Scroll down the page',
        'tooltip': 'Scroll down the page',
    },
    # datatable bindings - end
    'add_comment': {
        'keys': ['n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a comment',
    },
    'delete_comment': {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a comment',
    },
    'link_work_item': {
        'keys': ['n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Create a link between work items',
    },
    'view_work_item': {
        'keys': ['v'],
        'show': True,
        'description': 'Quick View',
        'tooltip': 'View details of a work item',
    },
    'unlink_work_item': {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a link between work items',
    },
    'add_remote_link': {
        'keys': ['n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a web link to a work item',
    },
    'delete_remote_link': {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a web link from a work item',
    },
    'create_work_item_subtask': {
        'keys': ['n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a subtask to a work item',
    },
    'edit_content': {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit the (text) content of a resource',
    },
    'open_text_editor': {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Open external editor',
    },
    'view_worklog': {
        'keys': ['ctrl+l', 'ctrl+t'],
        'show': True,
        'description': '\u231a',
        'tooltip': 'View the worklog of a work item',
    },
    'flag_work_item': {
        'keys': ['ctrl+f'],
        'show': True,
        'description': '\u2605',
        'tooltip': 'Flag a work item',
    },
    'log_work': {
        'keys': ['n'],
        'show': True,
        'description': '[+]',
        'tooltip': 'Log work done for a work item',
    },
    'open_in_browser': {
        'keys': ['ctrl+o'],
        'show': True,
        'description': '\u29c9',
        'tooltip': 'Open resource in the browser',
    },
    'delete_worklog': {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete worklog entry',
    },
    'edit_worklog_entry': {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit worklog entry',
    },
    'empty_recent_history': {
        'keys': ['d'],
        'show': True,
        'description': 'Empty History',
        'tooltip': 'Empty recent history',
    },
    'view_content': {
        'keys': ['v'],
        'show': True,
        'description': 'View Content',
        'tooltip': 'View the text content of a resource',
    },
    'copy_content': {
        'keys': ['c'],
        'show': True,
        'description': 'Copy Content',
        'tooltip': 'Copy the text content of a resource',
    },
    'save_content': {
        'keys': ['ctrl+s'],
        'show': True,
        'description': '\uf0c7',
        'tooltip': 'Save the text content of a resource',
    },
    'edit_jql': {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit JQL expressions',
    },
    'add_attachment': {
        'keys': ['ctrl+u', 'n'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Attach a file to a work item',
    },
    'open_attachment': {
        'keys': ['ctrl+o'],
        'show': True,
        'description': 'Open',
        'tooltip': 'Open attachment',
    },
    'delete_attachment': {
        'keys': ['d'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete attachment',
    },
}

KEY_BINDINGS_STANDARD = {
    # Help and Information
    'help': {'keys': ['f1'], 'show': True, 'description': '?', 'tooltip': 'Open the help'},
    'server_info': {
        'keys': ['f2'],
        'show': True,
        'description': 'Server',
        'tooltip': 'View details of your Jira server',
    },
    'config_info': {
        'keys': ['f3'],
        'show': True,
        'description': '\u2699',
        'tooltip': 'View the configuration file',
    },
    # Filter Focus - Alt+Letter (reliably works)
    'focus_project_filter': {
        'keys': ['alt+p'],
        'show': False,
        'description': 'Focuses the project dropdown',
        'tooltip': 'Focuses the project dropdown',
    },
    'focus_search_work_item_type_filter': {
        'keys': ['alt+t'],
        'show': False,
        'description': 'Focuses the work item types dropdown',
        'tooltip': 'Focuses the work item types dropdown',
    },
    'focus_search_work_item_status_filter': {
        'keys': ['alt+s'],
        'show': False,
        'description': 'Focuses the work item statuses dropdown',
        'tooltip': 'Focuses the work item statuses dropdown',
    },
    'focus_search_assignee_filter': {
        'keys': ['alt+a'],
        'show': False,
        'description': 'Focuses the assignee dropdown',
        'tooltip': 'Focuses the assignee dropdown',
    },
    'focus_search_work_item_key_filter': {
        'keys': ['alt+k'],
        'show': False,
        'description': 'Focuses the work item key search input',
        'tooltip': 'Focuses the work item key search input',
    },
    'focus_search_created_from_filter': {
        'keys': ['alt+c'],
        'show': False,
        'description': 'Focuses the created-from search input',
        'tooltip': 'Focuses the created-from search input',
    },
    'focus_search_created_until_filter': {
        'keys': ['alt+u'],
        'show': False,
        'description': 'Focuses the created-until search input',
        'tooltip': 'Focuses the created-until search input',
    },
    'focus_search_sort_filter': {
        'keys': ['alt+o'],
        'show': False,
        'description': 'Focuses the sorting search input',
        'tooltip': 'Focuses the sorting search input',
    },
    'focus_search_sprint_filter': {
        'keys': ['alt+v'],
        'show': False,
        'description': 'Focuses the active-sprint search input',
        'tooltip': 'Focuses the active-sprint search input',
    },
    'focus_search_jql': {
        'keys': ['alt+j'],
        'show': False,
        'description': 'Focuses the JQL search input',
        'tooltip': 'Focuses the JQL search input',
    },
    # Search Actions
    'search': {
        'keys': ['/'],
        'show': True,
        'description': '\uf002',
        'tooltip': 'Search work items',
    },
    'find_by_text': {
        'keys': ['ctrl+f'],
        'show': True,
        'description': 'Full-Text Search',
        'tooltip': 'Perform a full-text search of work items',
    },
    # Tab Navigation - use numbers (reliable)
    'focus_search_results': {
        'keys': ['1'],
        'show': False,
        'description': 'Focuses the search results table',
        'tooltip': 'Focuses the search results table',
    },
    'focus_work_item_information_tab': {
        'keys': ['2'],
        'show': False,
        'description': 'Focuses the work item information tab',
        'tooltip': 'Focuses the work item information tab',
    },
    'focus_work_item_details_tab': {
        'keys': ['3'],
        'show': False,
        'description': 'Focuses the work item details tab',
        'tooltip': 'Focuses the work item details tab',
    },
    'focus_work_item_comments_tab': {
        'keys': ['4'],
        'show': False,
        'description': 'Focuses the work item comments tab',
        'tooltip': 'Focuses the work item comments tab',
    },
    'focus_work_item_related_tab': {
        'keys': ['5'],
        'show': False,
        'description': 'Focuses the related work items tab',
        'tooltip': 'Focuses the related work items tab',
    },
    'focus_work_item_attachments_tab': {
        'keys': ['6'],
        'show': False,
        'description': 'Focuses the attachments tab',
        'tooltip': 'Focuses the attachments tab',
    },
    'focus_work_item_links_tab': {
        'keys': ['7'],
        'show': False,
        'description': 'Focuses the web links tab',
        'tooltip': 'Focuses the web links tab',
    },
    'focus_work_item_subtasks_tab': {
        'keys': ['8'],
        'show': False,
        'description': 'Focuses the work item subtasks tab',
        'tooltip': 'Focuses the work item subtasks tab',
    },
    # Item Creation
    'create_work_item': {
        'keys': ['ctrl+n'],
        'show': True,
        'description': 'New Item',
        'tooltip': 'Creates a new work item',
    },
    # History and Navigation
    'show_recent_history': {
        'keys': ['f4'],
        'show': True,
        'description': 'Recent',
        'tooltip': 'Shows the recent history',
    },
    'open_go_to_screen': {
        'keys': ['f5'],
        'show': True,
        'description': 'Related',
        'tooltip': 'View items related to the currently selected work item',
    },
    # Copy Actions (single letters work)
    'copy_issue_key': {
        'keys': ['y'],
        'show': True,
        'description': '\u2398 Key',
        'tooltip': 'Copy the work item key',
    },
    'copy_issue_url': {
        'keys': ['ctrl+c'],
        'show': True,
        'description': '\u2398 URL',
        'tooltip': 'Copy the work item URL',
    },
    'copy_content': {
        'keys': ['c'],
        'show': True,
        'description': 'Copy Content',
        'tooltip': 'Copy the text content of a resource',
    },
    # Git
    'create_git_branch': {
        'keys': ['f6'],
        'show': True,
        'description': 'Git',
        'tooltip': 'Creates a Git branch for a work item',
    },
    # Search Results Actions
    'filter': {
        'keys': ['f', '.'],
        'show': True,
        'description': 'Filter',
        'tooltip': 'Filter work items in the search results table',
    },
    'previous_issues_page': {
        'keys': ['['],
        'show': True,
        'description': '\uf060',
        'tooltip': 'Go to the previous page',
    },
    'next_issues_page': {
        'keys': [']'],
        'show': True,
        'description': '\uf061',
        'tooltip': 'Go to the next page',
    },
    'delete_work_item': {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Deletes a resource',
    },
    # DataTable Navigation - vim-style (hjkl)
    'select_cursor': {
        'keys': ['enter'],
        'show': False,
        'description': 'Select the item under the cursor',
        'tooltip': 'Select the item under the cursor',
    },
    'cursor_up': {
        'keys': ['up', 'k'],
        'show': False,
        'description': 'Move up',
        'tooltip': 'Move up',
    },
    'cursor_down': {
        'keys': ['down', 'j'],
        'show': False,
        'description': 'Move down',
        'tooltip': 'Move down',
    },
    'cursor_right': {
        'keys': ['right', 'l'],
        'show': False,
        'description': 'Move to the right',
        'tooltip': 'Move to the right',
    },
    'cursor_left': {
        'keys': ['left', 'h'],
        'show': False,
        'description': 'Move to the left',
        'tooltip': 'Move to the left',
    },
    'page_up': {
        'keys': ['ctrl+u'],
        'show': False,
        'description': 'Move 1 page up',
        'tooltip': 'Move 1 page up',
    },
    'page_down': {
        'keys': ['ctrl+d'],
        'show': False,
        'description': 'Move 1 page down',
        'tooltip': 'Move 1 page down',
    },
    'scroll_top': {
        'keys': ['g'],
        'show': False,
        'description': 'Scroll to the top',
        'tooltip': 'Scroll to the top',
    },
    'scroll_bottom': {
        'keys': ['G'],
        'show': False,
        'description': 'Scroll to the bottom',
        'tooltip': 'Scroll to the bottom',
    },
    'scroll_home': {
        'keys': ['g'],
        'show': False,
        'description': 'Scroll to the beginning',
        'tooltip': 'Scroll to the beginning',
    },
    'scroll_end': {
        'keys': ['G'],
        'show': False,
        'description': 'Scroll to the end',
        'tooltip': 'Scroll to the end',
    },
    'scroll_up': {
        'keys': ['up', 'k'],
        'show': False,
        'description': 'Scroll up the page',
        'tooltip': 'Scroll up the page',
    },
    'scroll_down': {
        'keys': ['down', 'j'],
        'show': False,
        'description': 'Scroll down the page',
        'tooltip': 'Scroll down the page',
    },
    # Comments
    'add_comment': {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a comment',
    },
    'delete_comment': {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a comment',
    },
    # Work Item Links
    'link_work_item': {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Create a link between work items',
    },
    'view_work_item': {
        'keys': ['v'],
        'show': True,
        'description': '\u2139',
        'tooltip': 'View details of a work item',
    },
    'unlink_work_item': {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a link between work items',
    },
    # Remote Links (Web Links)
    'add_remote_link': {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a web link to a work item',
    },
    'delete_remote_link': {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete a web link from a work item',
    },
    # Subtasks
    'create_work_item_subtask': {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Add a subtask to a work item',
    },
    # Content Editing
    'edit_content': {
        'keys': ['e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit the (text) content of a resource',
    },
    'open_text_editor': {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Open text editor',
    },
    'view_content': {
        'keys': ['v'],
        'show': True,
        'description': 'View Content',
        'tooltip': 'View the text content of a resource',
    },
    'save_content': {
        'keys': ['ctrl+s'],
        'show': True,
        'description': '\uf0c7',
        'tooltip': 'Save the text content of a resource',
    },
    'edit_jql': {
        'keys': ['ctrl+e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit JQL expressions',
    },
    # Worklog
    'view_worklog': {
        'keys': ['w'],
        'show': True,
        'description': '\u231a',
        'tooltip': 'View the worklog of a work item',
    },
    'log_work': {
        'keys': ['l'],
        'show': True,
        'description': '[+]',
        'tooltip': 'Log work done for a work item',
    },
    'delete_worklog': {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete worklog entry',
    },
    'edit_worklog_entry': {
        'keys': ['e'],
        'show': True,
        'description': '\u270e',
        'tooltip': 'Edit worklog entry',
    },
    # Flags
    'flag_work_item': {
        'keys': ['*'],
        'show': True,
        'description': '\u2605',
        'tooltip': 'Flag a work item',
    },
    # Browser and Attachments
    'open_in_browser': {
        'keys': ['o'],
        'show': True,
        'description': '\u2197',
        'tooltip': 'Open resource in the browser',
    },
    'add_attachment': {
        'keys': ['a'],
        'show': True,
        'description': '\u271a',
        'tooltip': 'Attach a file to a work item',
    },
    'open_attachment': {
        'keys': ['o'],
        'show': True,
        'description': '\u2197',
        'tooltip': 'Open attachment',
    },
    'delete_attachment': {
        'keys': ['x'],
        'show': True,
        'description': '\u2716',
        'tooltip': 'Delete attachment',
    },
    # History
    'empty_recent_history': {
        'keys': ['x'],
        'show': True,
        'description': 'Empty History',
        'tooltip': 'Empty recent history',
    },
}
