(use-cases)=
# Use Cases

This document contains UML sequence diagrams that model the primary use cases supported by JiraTUI. Each diagram
illustrates the interaction flow between user actions, the TUI/CLI interface, and the underlying Python classes that
orchestrate the communication with the Jira REST API.

Diagrams are organized into two main categories:

- **Work Item Operations**: Create, retrieve, delete, and search work items via keyword and full-text search. These
operations map directly to the Jira Cloud Platform REST API v3 (and v2 for on-premises installations).

- **Resource Management**: Manage ancillary resources tied to work items: comments (add, view, delete), related tasks,
web links, attachments, and subtasks. Additionally, covers work logging (time tracking) for work items, allowing
teams to record effort and view historical work logs.

Each sequence diagram references the relevant Python classes from the codebase. This helps maintainers and contributors
trace the flow from entry point through the application layers to API invocation.

## Search Work Items

(use-case-filter-based-search)=
### Filter-based Search

Using filter-based search the user needs to provide values for any of the filters (excluding the Work Item Key, see
below). After pressing `^r` the UI will fetch and show the details of the work items found that match the search
filters.

The following UML sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to search work items based on filters defined by the user.

The following are the main components used by the application to support this use case:

- [MainScreen](#jiratui.widgets.screen.MainScreen): Main orchestrator that handles search action and filter collection
- [ProjectSelectionInput](#jiratui.widgets.filters.ProjectSelectionInput), [IssueTypeSelectionInput](#jiratui.widgets.filters.IssueTypeSelectionInput), [IssueStatusSelectionInput](#jiratui.widgets.filters.IssueStatusSelectionInput): Filter widgets
- [JiraUserInput](#jiratui.widgets.commons.users.JiraUserInput): Assignee filter to filter item by assignee
- [IssueSearchCreatedFromWidget](#jiratui.widgets.filters.IssueSearchCreatedFromWidget), [IssueSearchCreatedUntilWidget](#jiratui.widgets.filters.IssueSearchCreatedUntilWidget): Date range filters
- [ActiveSprintCheckbox](#jiratui.widgets.filters.ActiveSprintCheckbox): Sprint filter to filter items in the current sprint.
- [JQLSearchWidget](#jiratui.widgets.filters.JQLSearchWidget): Advanced JQL expression filter
- [OrderByWidget](#jiratui.widgets.filters.OrderByWidget): Sort results
- [IssuesSearchResultsTable](#jiratui.widgets.search.IssuesSearchResultsTable): To display the results
- [APIController](#jiratui.api_controller.controller.APIController): API communication layer

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen
        participant APIController
        participant JiraAPI

        User->>MainScreen: Access Filter Widgets<br/>(Project, Assignee, Type, Status, etc.)
        Note over MainScreen: User can choose any filter combination:<br/>- Project<br/>- Issue Type<br/>- Status<br/>- Assignee<br/>- Work Item Key<br/>- Created From/Until<br/>- Active Sprint<br/>- JQL Expression<br/>- Order By

        User->>MainScreen: Set Filter 1 (optional)
        MainScreen->>MainScreen: Update Filter State
        Note right of MainScreen: User can set multiple<br/>filters in any order

        User->>MainScreen: Set Filter 2 (optional)
        MainScreen->>MainScreen: Update Filter State

        User->>MainScreen: Set Filter N (optional)
        MainScreen->>MainScreen: Update Filter State

        User->>MainScreen: Press Ctrl+R (Search)
        activate MainScreen
        MainScreen->>MainScreen: action_search()

        MainScreen->>MainScreen: Collect all filter values<br/>(project, assignee, type,<br/>status, dates, key, sprint)
        MainScreen->>MainScreen: Build search query<br/>(JQL or API parameters)

        MainScreen->>APIController: Execute search<br/>(with collected filters)
        activate APIController

        APIController->>JiraAPI: POST/GET search request<br/>(JQL or REST endpoint)
        activate JiraAPI

        JiraAPI-->>APIController: Return matched<br/>work items
        deactivate JiraAPI
        deactivate APIController

        MainScreen->>MainScreen: Process results<br/>(populate search table)

        deactivate MainScreen

        MainScreen->>User: Show filtered work items<br/>(with applied criteria)

        User->>MainScreen: Select work item from results<br/>(optional)
        MainScreen->>APIController: Fetch work item details
        APIController->>JiraAPI: GET work item details
        JiraAPI-->>APIController: Return full work item
        APIController-->>MainScreen: Return details
        MainScreen->>MainScreen: Populate detail tabs<br/>(Info, Comments, Attachments, etc.)
        MainScreen->>User: Display work item details
```
````

(use-case-text-based-search)=
### Full-Text Search

The following UML sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to search work items based on a full-text term.

The following are the main components used by the application to support this use case:

- [MainScreen](#jiratui.widgets.screen.MainScreen): Main screen that handles the `/` key binding and manages the flow
- [TextSearchScreen](#jiratui.widgets.text_search.TextSearchScreen): Modal screen for full-text search input and results display
- [APIController](#jiratui.api_controller.controller.APIController): API communication for executing the full-text search

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen
        participant TextSearchScreen
        participant APIController
        participant JiraAPI as Jira REST API

        User->>MainScreen: Press '/'
        activate MainScreen
        MainScreen->>MainScreen: action_find_by_text()

        MainScreen->>TextSearchScreen: push_screen(TextSearchScreen)
        activate TextSearchScreen

        TextSearchScreen->>User: Display full-text search input field<br/>(minimum term length validation)
        deactivate MainScreen

        User->>TextSearchScreen: Type search term<br/>(text query)
        Note right of TextSearchScreen: Real-time validation:<br/>- Check minimum term length<br/>- FULL_TEXT_SEARCH_DEFAULT_MINIMUM_TERM_LENGTH

        User->>TextSearchScreen: Press Enter (or trigger search)
        activate TextSearchScreen
        TextSearchScreen->>TextSearchScreen: Validate search term

        alt Term length valid
            TextSearchScreen->>TextSearchScreen: Build JQL query<br/>(or text search parameter)
            TextSearchScreen->>APIController: Execute search<br/>(with search term)
            activate APIController

            APIController->>JiraAPI: POST/GET search request<br/>(full-text search parameter)
            activate JiraAPI

            JiraAPI-->>APIController: Return matched work items
            deactivate JiraAPI
            deactivate APIController

            TextSearchScreen->>TextSearchScreen: Process results<br/>(format search results)
            TextSearchScreen->>User: Display search results<br/>(matching work items)

            User->>TextSearchScreen: Select work item from results<br/>(optional)
            TextSearchScreen->>TextSearchScreen: Prepare work item context<br/>(set as selected item)

            TextSearchScreen->>MainScreen: Return selected work item<br/>(pop_screen with result)
            deactivate TextSearchScreen
            activate MainScreen

            MainScreen->>MainScreen: Update search results table<br/>with returned work item

            MainScreen->>APIController: Fetch full work item details<br/>(if needed)
            MainScreen->>User: Display work item details<br/>in main screen tabs

        else Term length invalid
            TextSearchScreen->>User: Show validation error<br/>(term too short)
            Note right of TextSearchScreen: User must enter at least<br/>N characters
        end

        deactivate MainScreen
```
````

(use-case-work-item-search)=
### Search Single Work Item

To search a single work item the user needs to provide the item's key in the Work Item Key input field. After pressing
`^r` the UI will fetch and show the details of the work item or, an error message if the item can not be found.

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to search and retrieve an existing work item.

````{toggle}
```{mermaid}
    sequenceDiagram
        actor User
        participant MainScreen
        participant APIController
        participant JiraAPI

        User->>MainScreen: Set Work Item Key input filter
        MainScreen->>MainScreen: Update Filter State

        User->>MainScreen: Press ^r (Search)
        activate MainScreen
        MainScreen->>MainScreen: action_search()

        MainScreen->>APIController: Execute search<br/>(with collected filters)
        activate APIController

        APIController->>JiraAPI: POST/GET search request<br/>(JQL or REST endpoint)
        activate JiraAPI

        JiraAPI-->>APIController: Return matched<br/>work item
        deactivate JiraAPI
        deactivate APIController

        MainScreen->>MainScreen: Process results<br/>(populate search table)

        deactivate MainScreen

        MainScreen->>User: Show filtered work item

        User->>MainScreen: Select work item from results<br/>(optional)
        MainScreen->>APIController: Fetch work item details
        APIController->>JiraAPI: GET work item details
        JiraAPI-->>APIController: Return full work item
        APIController-->>MainScreen: Return details
        MainScreen->>MainScreen: Populate detail tabs<br/>(Info, Comments, Attachments, etc.)
        MainScreen->>User: Display work item details
```
````

(use-case-create-work-item)=
## Create Work Items

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to create a new work item.

The following are the main components used by the application to support this use case:

- [AddWorkItemScreen](#jiratui.widgets.create_work_item.screen.AddWorkItemScreen): Main screen that orchestrates the entire flow
- [WorkItemProjectSelectionField](#jiratui.widgets.create_work_item.fields.WorkItemProjectSelectionField): Project selector
- [WorkItemTypeSelectionField](#jiratui.widgets.create_work_item.fields.WorkItemTypeSelectionField): Issue type selector
- [SummaryField](#jiratui.widgets.create_work_item.fields.SummaryField): Summary input
- [ParentKeyField](#jiratui.widgets.create_work_item.fields.ParentKeyField): Parent work item key input
- [JiraUserInput](#jiratui.widgets.commons.users.JiraUserInput): Reporter and Assignee selectors
- [ADFMarkdownTextAreaWidget](#jiratui.widgets.commons.adf.ADFMarkdownTextAreaWidget), [PlainTextTextAreaWidget](#jiratui.widgets.commons.widgets.PlainTextTextAreaWidget): Description and custom textarea fields
- [LabelsWidget](#jiratui.widgets.commons.widgets.LabelsWidget), [MultiSelectWidget](#jiratui.widgets.commons.widgets.MultiSelectWidget), [SingleUserPickerWidget](#jiratui.widgets.commons.widgets.SingleUserPickerWidget), [MultiUserPickerWidget](#jiratui.widgets.commons.widgets.MultiUserPickerWidget): Dynamic custom fields
- [TextAreaTabbedContent](#jiratui.widgets.create_work_item.screen.TextAreaTabbedContent): Container for textarea fields with ^e key binding to open external editor

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen
        participant AddWorkItemScreen
        participant APIController
        participant JiraAPI as Jira REST API

        User->>MainScreen: Press '^n'
        activate MainScreen
        MainScreen->>MainScreen: action_create_work_item()

        MainScreen->>AddWorkItemScreen: push_screen(AddWorkItemScreen)
        activate AddWorkItemScreen

        AddWorkItemScreen->>APIController: on_mount(): Fetch available projects
        activate APIController
        APIController->>JiraAPI: GET /rest/api/3/projects
        JiraAPI-->>APIController: Return list of projects
        deactivate APIController

        AddWorkItemScreen->>User: Display create work item form<br/>(Project selector, Issue Type selector, etc.)
        deactivate MainScreen

        Note over AddWorkItemScreen: Form Fields:<br/>- Project (*)<br/>- Issue Type (*)<br/>- Reporter (*)<br/>- Assignee<br/>- Summary (*)<br/>- Description<br/>- Parent Key<br/>- Additional custom fields

        User->>AddWorkItemScreen: Select Project
        activate AddWorkItemScreen
        AddWorkItemScreen->>APIController: Fetch available issue types<br/>for selected project
        activate APIController
        APIController->>JiraAPI: GET /rest/api/3/issue/createmeta
        JiraAPI-->>APIController: Return issue types
        deactivate APIController
        AddWorkItemScreen->>User: Update Issue Type dropdown

        User->>AddWorkItemScreen: Select Issue Type
        AddWorkItemScreen->>APIController: Fetch issue create metadata<br/>(for project + issue type)
        activate APIController
        APIController->>JiraAPI: GET /rest/api/3/issue/createmeta<br/>(with project + issue type)
        JiraAPI-->>APIController: Return field metadata
        deactivate APIController

        AddWorkItemScreen->>AddWorkItemScreen: Build dynamic widgets<br/>(based on metadata)
        AddWorkItemScreen->>User: Display dynamic form fields<br/>(custom fields, labels, etc.)

        User->>AddWorkItemScreen: Fill required fields<br/>(in any order)
        Note right of AddWorkItemScreen: User provides:<br/>- Project<br/>- Issue Type<br/>- Summary<br/>- Reporter<br/>- Optional: Assignee, Description,<br/>Parent Key, Custom Fields

        AddWorkItemScreen->>AddWorkItemScreen: Validate required fields<br/>(on each field change)

        alt All required fields filled
            AddWorkItemScreen->>AddWorkItemScreen: Enable Save button
        else Missing required fields
            AddWorkItemScreen->>AddWorkItemScreen: Keep Save button disabled
        end

        User->>AddWorkItemScreen: Press '^s' or click Save
        activate AddWorkItemScreen
        AddWorkItemScreen->>AddWorkItemScreen: Validate all required fields

        alt Validation passed
            AddWorkItemScreen->>AddWorkItemScreen: Collect all field values<br/>(static + dynamic)
            AddWorkItemScreen->>AddWorkItemScreen: Format field values<br/>(user pickers, labels,<br/>select fields, etc.)

            AddWorkItemScreen->>AddWorkItemScreen: Build work item payload<br/>(fields: {...})

            AddWorkItemScreen->>MainScreen: pop_screen()<br/>(return payload data)
            deactivate AddWorkItemScreen
            activate MainScreen

            MainScreen->>APIController: Create work item<br/>(with payload)
            activate APIController
            APIController->>JiraAPI: POST /rest/api/3/issues<br/>(with work item payload)
            JiraAPI-->>APIController: Return created work item<br/>(with new key)
            deactivate APIController

            MainScreen->>MainScreen: Update search results<br/>(add new work item)

            MainScreen->>User: Display success notification<br/>(New work item created: KEY-123)
            deactivate MainScreen

        else Validation failed
            AddWorkItemScreen->>User: Show validation error<br/>(Fields marked with (*) required)
            deactivate AddWorkItemScreen
        end

        User->>AddWorkItemScreen: Press 'escape' or click Cancel<br/>(optional - dismiss without saving)
        AddWorkItemScreen->>MainScreen: pop_screen()<br/>(no payload)
        AddWorkItemScreen->>User: Return to main screen
```
````

(use-case-update-work-item)=
## Update Work Items

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to update an existing work item.

The following are the main components used by the application to support this use case:

- [IssueDetailsWidget](#jiratui.widgets.work_item_details.details.IssueDetailsWidget): Container for displaying work item information
- [JiraUserInput](#jiratui.widgets.commons.users.JiraUserInput), [SingleUserPickerWidget](#jiratui.widgets.commons.widgets.SingleUserPickerWidget): For user selection fields (Assignee, Reporter)
- [TextInputWidget](#jiratui.widgets.commons.widgets.TextInputWidget): For text-based fields
- [LabelsWidget](#jiratui.widgets.commons.widgets.LabelsWidget): For managing labels
- [NumericInputWidget](#jiratui.widgets.commons.widgets.NumericInputWidget)
- [DateInputWidget](#jiratui.widgets.commons.widgets.DateInputWidget)
- [DateTimeInputWidget](#jiratui.widgets.commons.widgets.DateTimeInputWidget)
- [SelectionWidget](#jiratui.widgets.commons.widgets.SelectionWidget)
- [URLWidget](#jiratui.widgets.commons.widgets.URLWidget)
- [MultiSelectWidget](#jiratui.widgets.commons.widgets.MultiSelectWidget)
- [MultiUserPickerWidget](#jiratui.widgets.commons.widgets.MultiUserPickerWidget)
- [APIController](#jiratui.api_controller.controller.APIController): API communication layer for field updates

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant DetailsTab
        participant EditFieldModal
        participant APIController
        participant JiraAPI

        Note over User,JiraAPI: User has already selected a work item<br/>and is viewing the Details tab

        User->>DetailsTab: View work item details
        activate DetailsTab

        DetailsTab->>DetailsTab: on_mount(): Load work item fields<br/>(from work item context)
        DetailsTab->>User: Display editable field widgets<br/>(clickable/selectable fields)

        User->>DetailsTab: Click on field to edit<br/>(e.g., Assignee, Status, Labels)
        activate DetailsTab

        alt Field is inline editable
            DetailsTab->>EditFieldModal: push_screen(EditFieldModal)<br/>or show inline edit widget
            activate EditFieldModal

            EditFieldModal->>APIController: on_mount(): Fetch field metadata<br/>(for allowed values)
            activate APIController
            APIController->>JiraAPI: GET /rest/api/3/issue/createmeta<br/>or GET /rest/api/3/fields/{fieldId}
            JiraAPI-->>APIController: Return field metadata<br/>(allowed values, constraints)
            deactivate APIController

            EditFieldModal->>User: Display edit form<br/>(field-specific widget:<br/>Dropdown, Text input, User picker, etc.)

        else Field requires external action
            DetailsTab->>User: Show validation message<br/>(e.g., "Cannot edit this field")
        end

        User->>EditFieldModal: Select/enter new value<br/>(based on field type)
        Note right of EditFieldModal: Field types:<br/>- Select (Status, Priority)<br/>- User picker (Assignee, Reporter)<br/>- Text (Summary, Description)<br/>- Labels, Components, etc.

        User->>EditFieldModal: Press '^s' or click Save
        activate EditFieldModal
        EditFieldModal->>EditFieldModal: Validate new value<br/>(against field constraints)

        alt Validation passed
            EditFieldModal->>EditFieldModal: Format field value<br/>(for API - user IDs, enums, etc.)

            EditFieldModal->>EditFieldModal: Build update payload<br/>(fields: {fieldId: value})

            EditFieldModal->>DetailsTab: pop_screen()<br/>(return new value + field ID)
            deactivate EditFieldModal
            activate DetailsTab

            DetailsTab->>APIController: Update work item field<br/>(with fieldId + new value)
            activate APIController
            APIController->>JiraAPI: PUT /rest/api/3/issues/{key}<br/>(with fields: {fieldId: value})
            activate JiraAPI

            JiraAPI-->>APIController: Return updated work item
            deactivate JiraAPI
            deactivate APIController

            DetailsTab->>DetailsTab: Update field widget state<br/>with new value
            DetailsTab->>User: Refresh Details display<br/>(show updated field value)
            DetailsTab->>User: Show success notification<br/>(Field updated successfully)

        else Validation failed
            EditFieldModal->>User: Show validation error<br/>(Invalid value for field)
            Note right of EditFieldModal: User must enter valid value
        end

        deactivate DetailsTab

        User->>DetailsTab: Continue editing other fields<br/>(optional - repeat flow)
        Note right of User: Can edit multiple fields<br/>in sequence

        User->>DetailsTab: Press 'escape' or click outside<br/>(optional - exit Details tab)
        DetailsTab->>User: Return to work item view
```
````

## Manage Comments

(use-case-add-comment)=
### Add Comment

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to add a new comment to an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User as User
        participant CommentUI as CommentsTab Widget
        participant CommentModal as AddCommentModal
        participant CommentHandler as CommentHandler
        participant JiraAPI as Jira API Client
        participant Storage as Comment Cache

        User->>CommentUI: Presses 'n' key in Comments tab
        CommentUI->>CommentModal: Create and display modal screen
        CommentModal->>User: Shows comment input form
        User->>CommentModal: Enters comment text
        User->>CommentModal: Presses 'Ctrl+s' to submit
        CommentModal->>CommentHandler: validate_and_submit_comment(text)

        alt Comment validation succeeds
            CommentHandler->>JiraAPI: POST /issues/{key}/comments
            JiraAPI-->>CommentHandler: Returns new comment with ID
            CommentHandler->>Storage: Update comment cache
            CommentHandler->>CommentUI: Refresh comments list
            CommentUI-->>User: Display new comment in list
        else Comment validation fails
            CommentHandler-->>CommentModal: Show error message
            CommentModal-->>User: Display validation error
            User->>CommentModal: Correct and resubmit
        end

        User->>CommentModal: Presses 'Escape' to close modal
        CommentModal-->>CommentUI: Close and return to Comments tab
```
````

(use-case-delete-comment)=
### Delete Comment

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to delete a comment from an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User as User
        participant CommentUI as CommentsTab Widget
        participant CommentDisplay as CommentDisplay Widget
        participant ConfirmModal
        participant CommentHandler
        participant JiraAPI
        participant Storage as Comment Cache

        User->>CommentUI: Navigate to specific comment
        CommentUI->>CommentDisplay: Highlight selected comment
        CommentDisplay-->>User: Display comment with 'd' key hint
        User->>CommentDisplay: Presses 'd' key to delete
        CommentDisplay->>ConfirmModal: Show confirmation dialog
        ConfirmModal-->>User: "Are you sure you want to delete this comment?"

        alt User confirms deletion
            User->>ConfirmModal: Presses 'y' or Enter to confirm
            ConfirmModal->>CommentHandler: delete_comment(comment_id)
            CommentHandler->>JiraAPI: DELETE /issues/{key}/comments/{comment_id}

            alt Deletion succeeds
                JiraAPI-->>CommentHandler: Returns 204 No Content
                CommentHandler->>Storage: Remove comment from cache
                CommentHandler->>CommentUI: Refresh comments list
                CommentUI-->>User: Remove deleted comment from display
                CommentUI-->>User: Show success notification
            else Deletion fails (permission/not found error)
                JiraAPI-->>CommentHandler: Returns error (403/404)
                CommentHandler-->>ConfirmModal: Show error message
                ConfirmModal-->>User: Display error
            end
        else User cancels deletion
            User->>ConfirmModal: Presses 'n' or Escape to cancel
            ConfirmModal-->>CommentUI: Close dialog without deleting
            CommentUI-->>User: Return to comments list
        end
```
````

JiraTUI allows users to add comments to an existing work item as well as to view and delete existing comments.

### View Comments

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to view the list of comments associated to an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User as User
        participant SearchResults
        participant MainScreen
        participant IssueCommentsWidget
        participant CommentLoader
        participant JiraAPI
        participant CommentCache as Comment Cache

        User->>SearchResults: Selects work item from list
        SearchResults->>MainScreen: RowSelected event triggered
        MainScreen->>MainScreen: Extract selected work item key
        MainScreen->>MainScreen: Check if different from current key

        alt Item already loaded
            MainScreen-->>User: Skip reload (same item)
        else Item not yet loaded
            MainScreen->>IssueCommentsWidget: Set issue_key property
            IssueCommentsWidget->>CommentLoader: Trigger load_comments(issue_key)
            CommentLoader->>JiraAPI: GET /issues/{key}?expand=changelog
            JiraAPI-->>CommentLoader: Returns issue with comments
            CommentLoader->>CommentCache: Cache comments for issue
            CommentLoader->>IssueCommentsWidget: Update comments property
            IssueCommentsWidget-->>User: Display comments list (read-only)
            User->>MainScreen: Presses key '4' to focus Comments tab
            MainScreen->>IssueCommentsWidget: Set focus to Comments tab
            IssueCommentsWidget-->>User: Display Comments tab with comment list
        end

        User->>IssueCommentsWidget: Navigate through comments (arrow keys)
        IssueCommentsWidget-->>User: Highlight selected comment details
```
````

## Manage Attachments

### View Attachments

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to view the files attached to an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant AttachmentsDataTable
        participant IssueAttachmentsWidget
        participant ConfirmationScreen
        participant APIController
        participant WorkItemData

        User->>AttachmentsDataTable: Select attachment row
        AttachmentsDataTable->>AttachmentsDataTable: on_data_table_row_selected()
        AttachmentsDataTable->>AttachmentsDataTable: store attachment_id and file_name

        User->>AttachmentsDataTable: Press Delete (or d)
        AttachmentsDataTable->>AttachmentsDataTable: action_delete_attachment()

        alt Attachment Selected
            AttachmentsDataTable->>IssueAttachmentsWidget: push_screen(ConfirmationScreen)
            activate ConfirmationScreen
            ConfirmationScreen->>User: Display "Are you sure you want to delete the file?"
            deactivate ConfirmationScreen

            User->>ConfirmationScreen: Confirm or Cancel
            ConfirmationScreen->>IssueAttachmentsWidget: handle_delete_choice(result)

            alt User Confirms Deletion
                IssueAttachmentsWidget->>IssueAttachmentsWidget: post_message(Deleted)
                IssueAttachmentsWidget->>IssueAttachmentsWidget: on_attachments_data_table_deleted()
                IssueAttachmentsWidget->>IssueAttachmentsWidget: run_worker(_delete_attachment)

                activate APIController
                IssueAttachmentsWidget->>APIController: delete_attachment(attachment_id)
                APIController-->>IssueAttachmentsWidget: APIControllerResponse(success)
                deactivate APIController

                alt API Call Successful
                    alt fetch_attachments_on_delete is True
                        IssueAttachmentsWidget->>APIController: get_issue(work_item_key, fields=['attachment'])
                        APIController-->>IssueAttachmentsWidget: APIControllerResponse(issue_data)
                        IssueAttachmentsWidget->>WorkItemData: update attachments list
                    else fetch_attachments_on_delete is False
                        IssueAttachmentsWidget->>IssueAttachmentsWidget: _update_attachments_after_delete(attachment_id)
                        IssueAttachmentsWidget->>AttachmentsDataTable: remove row by attachment_id
                    end
                    IssueAttachmentsWidget-->>User: Attachment deleted successfully"
                else API Call Failed
                    IssueAttachmentsWidget-->>User: Failed to delete the file
                end
            else User Cancels
                ConfirmationScreen->>User: Close dialog, no action taken
            end
        else No Attachment Selected
            AttachmentsDataTable-->>User: Select a row before attempting to delete the file
        end
```
````

(use-case-attach-file)=
### Attach File

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to attach a file to an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant IssueAttachmentsWidget
        participant AddAttachmentScreen
        participant DirectoryTree
        participant FileNameInputWidget
        participant Button
        participant APIController
        participant AttachmentsDataTable

        User->>IssueAttachmentsWidget: Press ^u or 'n'
        IssueAttachmentsWidget->>AddAttachmentScreen: push_screen(AddAttachmentScreen)
        activate AddAttachmentScreen
        AddAttachmentScreen->>AddAttachmentScreen: compose()
        AddAttachmentScreen->>DirectoryTree: render file browser
        AddAttachmentScreen->>FileNameInputWidget: render path input field
        AddAttachmentScreen->>Button: render Save & Cancel buttons
        deactivate AddAttachmentScreen

        User->>DirectoryTree: browse and select file
        DirectoryTree->>DirectoryTree: FileSelected event
        DirectoryTree->>FileNameInputWidget: populate with file path
        FileNameInputWidget->>Button: enable Save button

        User->>Button: Press Save button
        Button->>AddAttachmentScreen: handle_save()
        AddAttachmentScreen->>IssueAttachmentsWidget: dismiss(file_path)

        activate IssueAttachmentsWidget
        IssueAttachmentsWidget->>APIController: add_attachment(issue_key, file_path)
        activate APIController
        APIController-->>IssueAttachmentsWidget: APIControllerResponse(success, attachment)
        deactivate APIController

        alt Success
            IssueAttachmentsWidget->>IssueAttachmentsWidget: update attachments list
            IssueAttachmentsWidget->>IssueAttachmentsWidget: watch_attachments()
            IssueAttachmentsWidget->>AttachmentsDataTable: rebuild table with new attachment
            IssueAttachmentsWidget-->>User: Upload successful
        else Failure
            IssueAttachmentsWidget-->>User: Failed to attach file
        end
        deactivate IssueAttachmentsWidget
```
````

### Delete Attachment

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to delete an attachment from an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen
        participant TabbedContent
        participant IssueAttachmentsWidget
        participant APIController
        participant AttachmentsDataTable

        User->>MainScreen: Press '6'
        MainScreen->>TabbedContent: switch to attachments tab
        MainScreen->>IssueAttachmentsWidget: set issue_key of selected work item

        activate IssueAttachmentsWidget
        IssueAttachmentsWidget->>IssueAttachmentsWidget: issue_key setter
        deactivate IssueAttachmentsWidget

        Note over MainScreen,APIController: Fetch attachment data from API

        activate IssueAttachmentsWidget
        IssueAttachmentsWidget->>APIController: get_issue(work_item_key, fields=['attachment'])
        activate APIController
        APIController-->>IssueAttachmentsWidget: APIControllerResponse(issue_data)
        deactivate APIController

        IssueAttachmentsWidget->>IssueAttachmentsWidget: attachments = WorkItemAttachments(...)
        deactivate IssueAttachmentsWidget

        Note over IssueAttachmentsWidget,AttachmentsDataTable: Render attachments list

        activate IssueAttachmentsWidget
        IssueAttachmentsWidget->>IssueAttachmentsWidget: watch_attachments(data)

        alt Attachments exist
            IssueAttachmentsWidget->>AttachmentsDataTable: create table
            loop for each attachment
                IssueAttachmentsWidget->>AttachmentsDataTable: add_row(filename, size, date, author, type)
            end
            IssueAttachmentsWidget->>IssueAttachmentsWidget: mount(table)
            IssueAttachmentsWidget-->>User: Display attachments table with list of files
        else No attachments
            IssueAttachmentsWidget-->>User: Display empty widget
        end
        deactivate IssueAttachmentsWidget

        Note over User,AttachmentsDataTable: User can interact with table

        User->>AttachmentsDataTable: Highlight or Select row
        AttachmentsDataTable->>AttachmentsDataTable: store selected attachment metadata
        AttachmentsDataTable-->>User: Show file details
```
````

## Manage Web Links

### View Web Links

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to view the list of web links (aka. remote links) associated to an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen
        participant TabbedContent
        participant IssueRemoteLinksWidget
        participant APIController

        User->>MainScreen: Press '7'
        MainScreen->>TabbedContent: switch to links tab
        MainScreen->>IssueRemoteLinksWidget: set issue_key of selected work item

        activate IssueRemoteLinksWidget
        IssueRemoteLinksWidget->>IssueRemoteLinksWidget: issue_key setter triggered
        deactivate IssueRemoteLinksWidget

        Note over MainScreen,APIController: Fetch web links data from API

        activate IssueRemoteLinksWidget
        IssueRemoteLinksWidget->>APIController: get_issue(work_item_key, fields=['issuelinks'])
        activate APIController
        APIController-->>IssueRemoteLinksWidget: APIControllerResponse(issue_data)
        deactivate APIController

        IssueRemoteLinksWidget->>IssueRemoteLinksWidget: update remote_links reactive attribute
        deactivate IssueRemoteLinksWidget

        Note over IssueRemoteLinksWidget: Render web links list

        activate IssueRemoteLinksWidget
        alt Links exist
            IssueRemoteLinksWidget->>IssueRemoteLinksWidget: compose() or update widgets
            IssueRemoteLinksWidget-->>User: Display list of web links
        else No links
            IssueRemoteLinksWidget-->>User: Display empty state message
        end
        deactivate IssueRemoteLinksWidget

        Note over User,IssueRemoteLinksWidget: User can interact with links

        User->>IssueRemoteLinksWidget: Navigate through links
        IssueRemoteLinksWidget-->>User: Show link details
```
````

(use-case-add-web-link)=
### Add Web Link

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to add a new web link (aka. remote link) to an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        Actor User
        participant IssueRemoteLinksWidget
        participant AddRemoteLinkScreen
        participant RemoteLinkURLInputWidget
        participant RemoteLinkNameInputWidget
        participant APIController
        participant JiraAPI

        User->>IssueRemoteLinksWidget: Press 'n'
        activate IssueRemoteLinksWidget
        IssueRemoteLinksWidget->>IssueRemoteLinksWidget: action_add_remote_link()
        alt issue_key is set
            IssueRemoteLinksWidget->>AddRemoteLinkScreen: Create & Push Screen
            activate AddRemoteLinkScreen
            AddRemoteLinkScreen->>User: Display 'New Web Link' Modal
        else issue_key not set
            IssueRemoteLinksWidget->>User: Show Warning Notification
            deactivate IssueRemoteLinksWidget
        end

        User->>RemoteLinkURLInputWidget: Enter URL
        activate RemoteLinkURLInputWidget
        RemoteLinkURLInputWidget->>AddRemoteLinkScreen: Input.Blurred event
        AddRemoteLinkScreen->>AddRemoteLinkScreen: validate_url()
        deactivate RemoteLinkURLInputWidget

        User->>RemoteLinkNameInputWidget: Enter Title
        activate RemoteLinkNameInputWidget
        RemoteLinkNameInputWidget->>AddRemoteLinkScreen: Input.Changed event
        AddRemoteLinkScreen->>AddRemoteLinkScreen: validate_change()
        alt URL and Title both filled
            AddRemoteLinkScreen->>AddRemoteLinkScreen: Enable Save Button
        else Missing required fields
            AddRemoteLinkScreen->>AddRemoteLinkScreen: Disable Save Button
        end
        deactivate RemoteLinkNameInputWidget

        User->>AddRemoteLinkScreen: Press 'Save' Button
        activate AddRemoteLinkScreen
        AddRemoteLinkScreen->>AddRemoteLinkScreen: handle_save()
        AddRemoteLinkScreen->>IssueRemoteLinksWidget: Dismiss with {link_url, link_title}
        deactivate AddRemoteLinkScreen

        IssueRemoteLinksWidget->>IssueRemoteLinksWidget: add_link(data)
        IssueRemoteLinksWidget->>IssueRemoteLinksWidget: run_worker(create_link(data))
        activate IssueRemoteLinksWidget
        IssueRemoteLinksWidget->>APIController: create_issue_remote_link()
        activate APIController
        APIController->>JiraAPI: POST /issue/{key}/remotelink
        activate JiraAPI
        JiraAPI->>JiraAPI: Create Remote Link
        JiraAPI-->>APIController: Success/Error Response
        deactivate JiraAPI
        APIController-->>IssueRemoteLinksWidget: APIControllerResponse
        deactivate APIController

        alt Link created successfully
            IssueRemoteLinksWidget->>IssueRemoteLinksWidget: fetch_remote_links(issue_key)
            IssueRemoteLinksWidget->>IssueRemoteLinksWidget: Build IssueRemoteLinkCollapsible widgets
            IssueRemoteLinksWidget->>User: Display updated list of links
        else Link creation failed
            IssueRemoteLinksWidget->>User: Show Error Notification
        end
        deactivate IssueRemoteLinksWidget
```
````

(use-case-delete-web-link)=
### Delete Web Link

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to delete a web link (aka. remote link) from an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        Actor User
        participant IssueRemoteLinkCollapsible
        participant ConfirmationScreen
        participant IssueRemoteLinksWidget
        participant APIController
        participant JiraAPI

        User->>IssueRemoteLinkCollapsible: Press 'd'
        activate IssueRemoteLinkCollapsible
        IssueRemoteLinkCollapsible->>IssueRemoteLinkCollapsible: action_delete_remote_link()

        IssueRemoteLinkCollapsible->>ConfirmationScreen: Create & Push Screen
        activate ConfirmationScreen
        ConfirmationScreen->>User: Display confirmation modal

        alt User Confirms Deletion
            User->>ConfirmationScreen: Press 'y' (confirm)
            ConfirmationScreen-->>IssueRemoteLinkCollapsible: Callback with result=true
            deactivate ConfirmationScreen

            IssueRemoteLinkCollapsible->>IssueRemoteLinkCollapsible: handle_delete_choice(result=true)
            IssueRemoteLinkCollapsible->>IssueRemoteLinksWidget: Post Message: Deleted(work_item_key, link_id)

            activate IssueRemoteLinksWidget
            IssueRemoteLinksWidget->>IssueRemoteLinksWidget: on_issue_remote_link_collapsible_deleted(message)
            IssueRemoteLinksWidget->>IssueRemoteLinksWidget: run_worker(_delete_link(work_item_key, link_id))

            IssueRemoteLinksWidget->>APIController: delete_issue_remote_link(work_item_key, link_id)
            activate APIController
            APIController->>JiraAPI: DELETE /issue/{key}/remotelink/{id}
            activate JiraAPI
            JiraAPI->>JiraAPI: Delete Remote Link
            JiraAPI-->>APIController: Success/Error Response
            deactivate JiraAPI
            APIController-->>IssueRemoteLinksWidget: APIControllerResponse
            deactivate APIController

            alt Link deleted successfully
                IssueRemoteLinksWidget->>IssueRemoteLinksWidget: issue_key = issue_key (trigger watch)
                IssueRemoteLinksWidget->>IssueRemoteLinksWidget: fetch_remote_links(issue_key)
                IssueRemoteLinksWidget->>User: Display updated list
            else Link deletion failed
                IssueRemoteLinksWidget->>User: Show Error Notification
            end
            deactivate IssueRemoteLinksWidget
            deactivate IssueRemoteLinkCollapsible

        else User Cancels Deletion
            User->>ConfirmationScreen: Press 'n' (cancel)
            ConfirmationScreen-->>IssueRemoteLinkCollapsible: Callback with result=false
        end
```
````

## Manage Related Tasks

(use-case-relate-work-items)=
### Add Related Task

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to add a new task related to an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        Actor User
        participant RelatedIssuesWidget
        participant AddWorkItemRelationshipScreen
        participant IssueLinkTypeSelector
        participant LinkedWorkItemInputWidget
        participant APIController
        participant JiraAPI as Jira API
        participant RelatedIssueCollapsible as RelatedIssueCollapsible

        User->>RelatedIssuesWidget: Press 'n'
        activate RelatedIssuesWidget

        RelatedIssuesWidget->>AddWorkItemRelationshipScreen: Create & push screen<br/>with issue_key
        activate AddWorkItemRelationshipScreen

        AddWorkItemRelationshipScreen->>AddWorkItemRelationshipScreen: Compose UI<br/>(IssueLinkTypeSelector, LinkedWorkItemInputWidget, buttons)

        Note over AddWorkItemRelationshipScreen: on_mount triggered
        AddWorkItemRelationshipScreen->>AddWorkItemRelationshipScreen: run_worker(fetch_issue_link_types)
        activate IssueLinkTypeSelector

        AddWorkItemRelationshipScreen->>APIController: issue_link_types()
        activate APIController
        APIController->>JiraAPI: GET /rest/api/3/issueLinkType
        activate JiraAPI
        JiraAPI-->>APIController: List[LinkIssueType]
        deactivate JiraAPI
        deactivate APIController

        AddWorkItemRelationshipScreen->>IssueLinkTypeSelector: set_options(link_types)
        deactivate IssueLinkTypeSelector

        Note over User,RelatedIssueCollapsible: User fills in form
        User->>IssueLinkTypeSelector: Select link type<br/>(e.g., "blocks", "relates to")
        activate IssueLinkTypeSelector
        IssueLinkTypeSelector->>AddWorkItemRelationshipScreen: on_select.Changed event
        AddWorkItemRelationshipScreen->>AddWorkItemRelationshipScreen: validate_relationship()
        AddWorkItemRelationshipScreen->>AddWorkItemRelationshipScreen: Enable save_button if<br/>both fields valid
        deactivate IssueLinkTypeSelector

        User->>LinkedWorkItemInputWidget: Enter work item key<br/>(e.g., "ABC-1234")
        activate LinkedWorkItemInputWidget
        LinkedWorkItemInputWidget->>AddWorkItemRelationshipScreen: on_input.Changed event
        AddWorkItemRelationshipScreen->>AddWorkItemRelationshipScreen: validate_change()
        AddWorkItemRelationshipScreen->>AddWorkItemRelationshipScreen: Enable save_button if<br/>both fields valid
        deactivate LinkedWorkItemInputWidget

        User->>AddWorkItemRelationshipScreen: Click 'Save' button
        AddWorkItemRelationshipScreen->>AddWorkItemRelationshipScreen: handle_save()
        AddWorkItemRelationshipScreen->>AddWorkItemRelationshipScreen: Extract link_type_id<br/>& link_type from selection
        AddWorkItemRelationshipScreen->>AddWorkItemRelationshipScreen: dismiss() with data dict
        deactivate AddWorkItemRelationshipScreen

        Note over RelatedIssuesWidget: callback triggered
        RelatedIssuesWidget->>RelatedIssuesWidget: add_relationship(data)
        RelatedIssuesWidget->>RelatedIssuesWidget: run_worker(link_work_items)
        activate RelatedIssuesWidget

        RelatedIssuesWidget->>APIController: link_work_items()
        activate APIController
        APIController->>JiraAPI: POST /rest/api/3/issueLink
        activate JiraAPI
        JiraAPI-->>APIController: Success/Error response
        deactivate JiraAPI
        deactivate APIController

        alt Success
            RelatedIssuesWidget->>User: Work items linked successfully

            RelatedIssuesWidget->>APIController: get_issue(issue_key,<br/>fields=['issuelinks'])
            activate APIController
            APIController->>JiraAPI: GET /rest/api/3/issue/{key}?fields=issuelinks
            activate JiraAPI
            JiraAPI-->>APIController: JiraIssue with related_issues
            deactivate JiraAPI
            deactivate APIController

            RelatedIssuesWidget->>RelatedIssuesWidget: update list of issues
            RelatedIssuesWidget->>RelatedIssuesWidget: Remove old children

            loop For each related_issue
                RelatedIssuesWidget->>RelatedIssueCollapsible: Create & mount<br/>RelatedIssueCollapsible
            end

            RelatedIssueCollapsible-->>User: Display new related task<br/>in the list
        else Failure
            RelatedIssuesWidget->>User: Failed to link
        end

        deactivate RelatedIssuesWidget
        deactivate RelatedIssuesWidget
```
````

### Delete Related Task

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to delete a related task from an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        Actor User
        participant RelatedIssueCollapsible as RelatedIssueCollapsible
        participant ConfirmationScreen as ConfirmationScreen
        participant APIController as APIController<br/>(app.api)
        participant JiraAPI as Jira API
        participant RelatedIssuesWidget as RelatedIssuesWidget

        User->>RelatedIssueCollapsible: Press 'd' (unlink_work_item)
        activate RelatedIssueCollapsible

        RelatedIssueCollapsible->>ConfirmationScreen: push_screen with<br/>confirmation message
        activate ConfirmationScreen
        ConfirmationScreen-->>User: Display confirmation dialog:<br/>'Are you sure you want to delete<br/>the link between the issues?'

        User->>ConfirmationScreen: Click 'Yes' button
        ConfirmationScreen->>RelatedIssueCollapsible: handle_delete_choice(result=True)
        deactivate ConfirmationScreen
        deactivate RelatedIssueCollapsible

        activate RelatedIssueCollapsible
        RelatedIssueCollapsible->>RelatedIssueCollapsible: run_worker(delete_link())
        activate RelatedIssueCollapsible

        RelatedIssueCollapsible->>APIController: delete_issue_link(link_id)
        activate APIController
        APIController->>JiraAPI: DELETE /rest/api/3/issueLink/{linkId}
        activate JiraAPI
        JiraAPI-->>APIController: Success/Error response
        deactivate JiraAPI
        deactivate APIController

        alt Success
            RelatedIssueCollapsible->>User: Link deleted successfully
            RelatedIssueCollapsible->>RelatedIssuesWidget: post_message(LinkDeleted(link_id))

            activate RelatedIssuesWidget
            RelatedIssuesWidget->>RelatedIssuesWidget: _refresh_issues_after_delete()
            RelatedIssuesWidget->>RelatedIssuesWidget: Filter out deleted link<br/>from self.issues list<br/>(remove by link_id)

            Note over RelatedIssuesWidget: watch_issues triggered by<br/>reactive property update
            RelatedIssuesWidget->>RelatedIssuesWidget: watch_issues()
            RelatedIssuesWidget->>RelatedIssuesWidget: remove_children()

            loop For each remaining related_issue
                RelatedIssuesWidget->>RelatedIssuesWidget: Create & mount<br/>RelatedIssueCollapsible
            end

            RelatedIssuesWidget-->>User: Updated list display<br/>(deleted item removed)
            deactivate RelatedIssuesWidget
        else Failure
            RelatedIssueCollapsible->>User: Failed to delete the link
        end

        deactivate RelatedIssueCollapsible
        deactivate RelatedIssueCollapsible
```
````

### View Related Tasks

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to view the list of tasks related to an existing work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        Actor User
        participant MainScreen
        participant RelatedIssuesWidget

        User->>MainScreen: Press '5'
        activate MainScreen

        Note over MainScreen: Assuming work item is<br/>already selected in results table

        MainScreen->>RelatedIssuesWidget: Focus widget
        activate RelatedIssuesWidget

        Note over RelatedIssuesWidget: issue_key & issues<br/>already set from<br/>previous selection

        RelatedIssuesWidget->>RelatedIssuesWidget: watch_issues() triggered<br/>(if not already displayed)
        activate RelatedIssuesWidget

        RelatedIssuesWidget->>RelatedIssuesWidget: remove_children()

        alt issues is None or Empty
            RelatedIssuesWidget-->>User: Display empty state
        else issues has related items
            loop For each RelatedJiraIssue in issues
                RelatedIssuesWidget->>RelatedIssuesWidget: Create RelatedIssueCollapsible<br/>with summary & link
                RelatedIssuesWidget->>RelatedIssuesWidget: Set border style<br/>based on priority
                RelatedIssuesWidget->>RelatedIssuesWidget: mount_all(collapsibles)
            end

            RelatedIssuesWidget-->>User: Display list of<br/>related tasks
        end

        deactivate RelatedIssuesWidget

        Note over RelatedIssuesWidget: (Optional) User scrolls<br/>through the list
        User->>RelatedIssuesWidget: Scroll/Navigate items

        deactivate RelatedIssuesWidget
        deactivate MainScreen
```
````

## Manage Log Work

### View Item Work Log

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to view the work logged for a selected work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant IssueDetailsWidget
        participant WorkItemWorkLogScreen
        participant APICtrl as APIController
        participant Jira as JiraAPI

        User->>IssueDetailsWidget: Press ^l
        activate IssueDetailsWidget
        IssueDetailsWidget->>WorkItemWorkLogScreen: show modal screen
        deactivate IssueDetailsWidget
        activate WorkItemWorkLogScreen

        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Mount screen
        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Start worker to fetch_work_log()

        WorkItemWorkLogScreen->>APICtrl: Call get_work_item_worklog(work_item_key)
        deactivate WorkItemWorkLogScreen
        activate APICtrl

        APICtrl->>Jira: GET worklogs for work item
        deactivate APICtrl
        activate Jira

        Jira->>Jira: Query worklogs and pagination
        Jira-->>APICtrl: Return PaginatedJiraWorklog with logs list
        deactivate Jira
        activate APICtrl

        APICtrl-->>WorkItemWorkLogScreen: Return APIControllerResponse with result
        deactivate APICtrl
        activate WorkItemWorkLogScreen

        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Extract worklog list from response
        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Set worklog_counter and worklog_total_count
        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Update subtitle with counts

        loop For each worklog in logs
            WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Build WorkLogCollapsible widget
            WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Create DataTable with worklog details
            WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Add rows with details
            WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Mount WorkLogCollapsible to container
        end

        WorkItemWorkLogScreen->>User: Display list of worklogs in collapsible widgets
        deactivate WorkItemWorkLogScreen

        User->>WorkItemWorkLogScreen: (Optional) Press Ctrl+O on worklog
        activate WorkItemWorkLogScreen
        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Open worklog URL in default browser
        deactivate WorkItemWorkLogScreen

        User->>WorkItemWorkLogScreen: (Optional) Press D on worklog
        activate WorkItemWorkLogScreen
        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Start worker to delete worklog
        WorkItemWorkLogScreen->>APICtrl: Call remove_worklog(work_item_key, worklog_id)
        deactivate WorkItemWorkLogScreen
        activate APICtrl

        APICtrl->>Jira: DELETE worklog
        deactivate APICtrl
        activate Jira

        Jira->>Jira: Remove worklog entry
        Jira-->>APICtrl: Success response
        deactivate Jira
        activate APICtrl

        APICtrl-->>WorkItemWorkLogScreen: Return APIControllerResponse
        deactivate APICtrl
        activate WorkItemWorkLogScreen

        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Notify "Worklog deleted"
        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Hide WorkLogCollapsible (display: none)
        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Update counters and subtitle
        WorkItemWorkLogScreen->>WorkItemWorkLogScreen: Set work_logs_deleted = true
        deactivate WorkItemWorkLogScreen

        User->>WorkItemWorkLogScreen: Press Escape to close
        activate WorkItemWorkLogScreen
        WorkItemWorkLogScreen->>IssueDetailsWidget: Dismiss with work_logs_deleted flag
        deactivate WorkItemWorkLogScreen
        activate IssueDetailsWidget

        IssueDetailsWidget->>IssueDetailsWidget: Check if work_logs_deleted is true

        alt work_logs_deleted == true
            IssueDetailsWidget->>APICtrl: Call get_issue() to refresh
            deactivate IssueDetailsWidget
            activate APICtrl
            APICtrl->>Jira: GET issue details
            Jira-->>APICtrl: Return updated issue
            APICtrl-->>DetaIssueDetailsWidgetils: Return updated JiraIssue
            deactivate APICtrl
            activate IssueDetailsWidget
            IssueDetailsWidget->>IssueDetailsWidget: Update work item details
        end

        deactivate IssueDetailsWidget
```
````

(use-case-log-work)=
### Log Work for Item

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes to log work for a selected work item.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant IssueDetailsWidget
        participant LogWorkScreen
        participant APICtrl as APIController
        participant Jira as JiraAPI

        User ->> IssueDetailsWidget: Press ^t
        activate IssueDetailsWidget
        IssueDetailsWidget->>LogWorkScreen: Push LogWorkScreen with work_item.key and current_remaining_estimate
        deactivate IssueDetailsWidget
        activate LogWorkScreen

        LogWorkScreen->>User: Display form (Time Spent, Time Remaining, Date Started, Work Description)

        User->>LogWorkScreen: Enter time spent value
        activate User
        LogWorkScreen->>LogWorkScreen: Validate time format
        LogWorkScreen->>LogWorkScreen: Enable/disable related fields and save button
        deactivate User

        User->>LogWorkScreen: (Optional) Enter time remaining
        activate User
        LogWorkScreen->>LogWorkScreen: Validate time format
        deactivate User

        User->>LogWorkScreen: (Optional) Add work description
        User->>LogWorkScreen: Click Save

        LogWorkScreen->>IssueDetailsWidget: Dismiss with form data dict
        deactivate LogWorkScreen
        activate IssueDetailsWidget

        IssueDetailsWidget->>IssueDetailsWidget: Extract data from result dict
        IssueDetailsWidget->>IssueDetailsWidget: Start worker for async execution

        IssueDetailsWidget->>APICtrl: Call add_work_item_worklog()
        deactivate IssueDetailsWidget
        activate APICtrl

        APICtrl->>APICtrl: Convert local datetime to UTC
        APICtrl->>Jira: POST worklog with time_spent, time_remaining, started, comment
        deactivate APICtrl
        activate Jira

        Jira->>Jira: Create worklog entry and update time tracking
        Jira-->>APICtrl: Success response
        deactivate Jira
        activate APICtrl

        APICtrl-->>IssueDetailsWidget: Return APIControllerResponse
        deactivate APICtrl
        activate IssueDetailsWidget

        IssueDetailsWidget->>IssueDetailsWidget: Check response.success
        IssueDetailsWidget->>User: Notify "Work logged successfully"

        IssueDetailsWidget->>APICtrl: Call get_issue() to refresh
        deactivate IssueDetailsWidget
        activate APICtrl
        APICtrl->>Jira: GET issue details
        Jira-->>APICtrl: Return updated issue
        APICtrl-->>IssueDetailsWidget: Return updated JiraIssue
        deactivate APICtrl
        activate IssueDetailsWidget

        IssueDetailsWidget->>IssueDetailsWidget: Update form fields with refreshed data
        IssueDetailsWidget->>IssueDetailsWidget: Re-render time tracking widget
        deactivate IssueDetailsWidget
```
````

(use-case-recent-history)=
## Recent History

### View Recent History

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes when the user wants to see the list of recently-viewed/updated/created work items.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen as Main Screen
        participant HistoryScreen
        participant HistoryManager
        participant HistoryWorkItemsTable

        User->>MainScreen: Presses 'alt+h' key
        MainScreen->>MainScreen: open recent history screen
        HistoryScreen->>HistoryManager: get the history entries
        HistoryManager->>HistoryScreen: entries
        HistoryScreen->>HistoryWorkItemsTable: build and populate table
        User-->>HistoryScreen: interacts with the screen commands
        HistoryScreen-->>User: commands responses
        User->>HistoryScreen: press 'escape'
        HistoryScreen->>HistoryScreen: dismiss and close
```
````

### Delete Recent History

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes when the user wants to delete the recent history.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen as Main Screen
        participant HistoryScreen
        participant HistoryManager
        participant HistoryWorkItemsTable

        User->>MainScreen: Presses 'alt+h' key
        MainScreen->>HistoryScreen: open recent history screen
        HistoryScreen->>HistoryManager: get the history entries
        HistoryManager->>HistoryScreen: entries
        HistoryScreen->>HistoryWorkItemsTable: build and populate table
        User->>HistoryScreen: press 'd'
        HistoryScreen->>HistoryManager: empty history
        HistoryScreen->>HistoryScreen: refresh table
```
````

### Copy Item Key from Recent History

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes when the user wants to copy the key of an item in the recent history.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen as Main Screen
        participant HistoryScreen
        participant HistoryManager
        participant HistoryWorkItemsTable

        User->>MainScreen: Presses 'alt+h' key
        MainScreen->>HistoryScreen: open recent history screen
        HistoryScreen->>HistoryManager: get the history entries
        HistoryManager->>HistoryScreen: entries
        HistoryScreen->>HistoryWorkItemsTable: build and populate table
        User->>HistoryWorkItemsTable: selects item A
        User->>HistoryWorkItemsTable: press '^k'
        HistoryWorkItemsTable->>HistoryWorkItemsTable: copy key to clippboard
```
````

### Copy Item URL from Recent History

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes when the user wants to copy the URL of an item in the recent history.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen as Main Screen
        participant HistoryScreen
        participant HistoryManager
        participant HistoryWorkItemsTable

        User->>MainScreen: Presses 'alt+h' key
        MainScreen->>HistoryScreen: open recent history screen
        HistoryScreen->>HistoryManager: get the history entries
        HistoryManager->>HistoryScreen: entries
        HistoryScreen->>HistoryWorkItemsTable: build and populate table
        User->>HistoryWorkItemsTable: selects item A
        User->>HistoryWorkItemsTable: press '^j'
        HistoryWorkItemsTable->>HistoryWorkItemsTable: copy URL to clippboard
```
````

### Open with Browser an Item from Recent History

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes when the user wants to open the URL of an item in the recent history in the browser.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen as Main Screen
        participant HistoryScreen
        participant HistoryManager
        participant HistoryWorkItemsTable

        User->>MainScreen: Presses 'alt+h' key
        MainScreen->>HistoryScreen: open recent history screen
        HistoryScreen->>HistoryManager: get the history entries
        HistoryManager->>HistoryScreen: entries
        HistoryScreen->>HistoryWorkItemsTable: build and populate table
        User->>HistoryWorkItemsTable: selects item A
        User->>HistoryWorkItemsTable: press '^o'
        HistoryWorkItemsTable->>HistoryWorkItemsTable: open URL
```
````

### Search Item from Recent History

The following sequence diagram depicts the interaction of the user with the application and the series of steps that
the application takes when the user wants to search/fetch an item from the recent history.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant MainScreen as Main Screen
        participant HistoryScreen
        participant HistoryManager
        participant HistoryWorkItemsTable

        User->>MainScreen: Presses 'alt+h' key
        MainScreen->>HistoryScreen: open recent history screen
        HistoryScreen->>HistoryManager: get the history entries
        HistoryManager->>HistoryScreen: entries
        HistoryScreen->>HistoryWorkItemsTable: build and populate table
        User->>HistoryWorkItemsTable: selects item A with key 'key-1'
        User->>HistoryWorkItemsTable: press 'enter'
        HistoryWorkItemsTable->>HistoryScreen: post_message('key-1')
        HistoryScreen->>HistoryScreen: dismiss('key-1')
        HistoryScreen->>MainScreen: pass control back to the main screen
        MainScreen->>MainScreen: set the value of the work item filter to 'key-1'
        MainScreen->>MainScreen: action_search()
        MainScreen->>User: show search result
```
````

(use-case-goto-screen)=
## Access Related Work Items Using the Go-To Screen

The use case describe the interaction of the user with the application while using the Go-To feature. The feature allows
users to easily jump to items related to a pre-selected work item. When enabled, this feature can be accessed by
pressing the corresponding key from 3 different locations:

- the search results table.
- the list of related tasks as seen in the "Related" tab.
- the list of subtasks as seen in the "Subtasks" tab.

(use-case-search-results-goto-screen)=
### Open Go-To Screen from Search Results

Use case describing the interaction between the user and the application when the user wants to open the Go-To screen
after selecting an item from the search results table.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant IssuesSearchResultsTable
        participant GoToScreen
        participant APIController
        participant API

        Note right of User: main screen is showing<br> a list of work items<br> in the search results
        User->>IssuesSearchResultsTable: selects work item A from the table
        User->>IssuesSearchResultsTable: Presses 'f6' key
        IssuesSearchResultsTable->>GoToScreen: open Go-To screen
        activate GoToScreen
        GoToScreen->>APIController: get issue A
        activate APIController
        APIController->>API: get issue A
        deactivate APIController
        activate API
        API->>APIController: issue A details
        activate APIController
        deactivate API
        APIController->>GoToScreen: issue A details
        deactivate APIController
        GoToScreen->>APIController: get parent of A
        activate APIController
        APIController->>API: get parent of A
        deactivate APIController
        activate API
        API->>APIController: parent of A
        deactivate API
        activate APIController
        APIController->>GoToScreen: parent of A
        deactivate APIController
        GoToScreen->>APIController: get subtasks of item A
        activate APIController
        APIController->>API: get subtasks of item A
        deactivate APIController
        activate API
        API->>APIController: subtasks
        deactivate API
        activate APIController
        APIController->>GoToScreen: subtasks
        deactivate APIController
        GoToScreen->>GoToScreen: populate data tables
        deactivate GoToScreen
```
````

(use-case-subtasks-goto-screen)=
### Open Go-To Screen from Subtasks Tab

Use case describing the interaction between the user and the application when the user wants to open the Go-To screen
after selecting an item in the Subtasks tab.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant ChildWorkItemCollapsible
        participant GoToScreen
        participant APIController
        participant API

        Note right of User: main screen is showing<br> a list of work items<br> in the "Subtasks" tab
        User->>ChildWorkItemCollapsible: selects work item A from the table
        User->>ChildWorkItemCollapsible: Presses 'f6' key
        ChildWorkItemCollapsible->>GoToScreen: open Go-To screen
        activate GoToScreen
        GoToScreen->>APIController: get issue A
        activate APIController
        APIController->>API: get issue A
        deactivate APIController
        activate API
        API->>APIController: issue A details
        activate APIController
        deactivate API
        APIController->>GoToScreen: issue A details
        deactivate APIController

        GoToScreen->>APIController: get parent of A
        activate APIController
        APIController->>API: get parent of A
        deactivate APIController
        activate API
        API->>APIController: parent of A
        deactivate API
        activate APIController
        APIController->>GoToScreen: parent of A
        deactivate APIController

        GoToScreen->>APIController: get subtasks of item A
        activate APIController
        APIController->>API: get subtasks of item A
        deactivate APIController
        activate API
        API->>APIController: subtasks
        deactivate API
        activate APIController
        APIController->>GoToScreen: subtasks
        deactivate APIController
        GoToScreen->>GoToScreen: populate data tables
        deactivate GoToScreen
```
````

(use-case-related-tasks-goto-screen)=
### Open Go-To Screen from Related Tasks Tab

Use case describing the interaction between the user and the application when the user wants to open the Go-To screen
after selecting an item in the Related tab.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant RelatedIssueCollapsible
        participant GoToScreen
        participant APIController
        participant API

        Note right of User: main screen is showing<br> a list of work items<br> in the "Related" tab
        User->>RelatedIssueCollapsible: selects work item A from the table
        User->>RelatedIssueCollapsible: Presses 'f6' key
        RelatedIssueCollapsible->>GoToScreen: open Go-To screen
        activate GoToScreen
        GoToScreen->>APIController: get issue A
        activate APIController
        APIController->>API: get issue A
        deactivate APIController
        activate API
        API->>APIController: issue A details
        activate APIController
        deactivate API
        APIController->>GoToScreen: issue A details
        deactivate APIController
        GoToScreen->>APIController: get parent of A
        activate APIController
        APIController->>API: get parent of A
        deactivate APIController
        activate API
        API->>APIController: parent of A
        deactivate API
        activate APIController
        APIController->>GoToScreen: parent of A
        deactivate APIController
        GoToScreen->>APIController: get subtasks of item A
        activate APIController
        APIController->>API: get subtasks of item A
        deactivate APIController
        activate API
        API->>APIController: subtasks
        deactivate API
        activate APIController
        APIController->>GoToScreen: subtasks
        deactivate APIController
        GoToScreen->>GoToScreen: populate data tables
        deactivate GoToScreen
```
````

(use-case-search-and-fetch-item-goto-screen)=
### Search and Fetch Item Selected in the Go-To Screen

Use case describing the interaction between the user and the application when the user opens the Go-To screen and
selects a work item in any of the tables on the screen.

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant GoToScreen
        participant IssuesSearchResultsTable
        participant MainScreen

        User->>IssuesSearchResultsTable: selects item with key 1
        IssuesSearchResultsTable->>GoToScreen: open screen
        GoToScreen->>GoToItemsTable: fills in table
        User->>GoToItemsTable: selects item witk key A from any of the tables
        activate GoToItemsTable
        User->>GoToItemsTable: press 'enter'
        GoToItemsTable->>GoToScreen: post_message(WorkItemSelected('A'))
        activate GoToScreen
        deactivate GoToItemsTable
        GoToScreen->>GoToScreen: dismiss('A')
        deactivate GoToScreen
        GoToScreen->>IssuesSearchResultsTable: dismissed with key A
        activate IssuesSearchResultsTable
        IssuesSearchResultsTable->>MainScreen: search and fetch item with key A
        deactivate IssuesSearchResultsTable
```
````

### Copy the Key of an Item from the Go-To Screen

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant GoToScreen
        participant Application
        participant GoToItemsTable
        User->>GoToItemsTable: highlight item with key 1 from the table
        GoToItemsTable->>GoToItemsTable: register the highlight
        User->>GoToItemsTable: press '^k'
        GoToItemsTable->>Application: copy key to the clippboard
        GoToItemsTable->>GoToScreen: display message "Key copied!"
```
````

### Copy the URL of an Item from the Go-To Screen

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant GoToScreen
        participant Application
        participant GoToItemsTable
        User->>GoToItemsTable: highlight item with key 1 from the table
        GoToItemsTable->>GoToItemsTable: register the highlight
        User->>GoToItemsTable: press '^j'
        GoToItemsTable->>Application: copy URL to the clippboard
        GoToItemsTable->>GoToScreen: display message "URL copied!"
```
````

### Open in Browser an Item from the Go-To Screen

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
    ---
    sequenceDiagram
        actor User
        participant GoToScreen
        participant Application
        participant GoToItemsTable
        User->>GoToItemsTable: highlight item with key 1 from the table
        GoToItemsTable->>GoToItemsTable: register the highlight
        User->>GoToItemsTable: press '^o'
        GoToItemsTable->>Application: open_url(url)
        GoToItemsTable->>GoToScreen: display message "Opening URL"
```
````
