<style>
.wy-nav-content {
    max-width: 100% !important;
}
</style>
(architecture)=
# Architecture

The following C4 diagrams summarize the most important components that make up JiraTUI. JiraTUI's architecture is
built to support users interact with their Jira instance across different [use cases](use-cases.md).

## C4 Context Diagram - JiraTUI

```{mermaid}
C4Context
    title JiraTUI - C4 Context Diagram
    Person(user, "Developer/User", "Interacts with Jira through terminal")
    System(jiratui, "JiraTUI", "Terminal User Interface & CLI")
    System_Ext(jira_api, "Atlassian Jira API", "REST API for accessing Jira Cloud/Data Center")
    Rel(user, jiratui, "Uses", "CLI commands / TUI interface")
    Rel(jiratui, jira_api, "Makes API calls", "HTTP/REST")
    Rel(jira_api, jiratui, "Returns Work Items Data", "JSON responses")
```

## C4 Container Diagram - JiraTUI

```{mermaid}
C4Container
    title JiraTUI - C4 Container Diagram

    Person(user, "Developer/User", "Interacts with Jira through terminal")

    Container_Boundary(c1, "JiraTUI") {
        Container(ui, "UI Application", "Python/Textual", "Provides UI components to interact with Jira")
        Container(cli, "CLI Application", "Python", "Provides CLI Commands to interact with Jira")
        Container(api, "API", "Python", "Implements Jira REST API's Endpoints")
        Container(controller, "API Controller", "Python", "Provides functionality for managing Jira resources")
    }

    System_Ext(jira_api, "Atlassian Jira API", "REST API for accessing Jira Cloud/Data Center")

    Rel(ui, controller, "Uses", "")
    Rel(cli, controller, "Uses", "")
    Rel(api, jira_api, "Requests/Responses", "HTTPS")
    Rel(user, cli, "Uses", "")
    Rel(user, ui, "Uses", "")
    Rel(controller, api, "Uses", "")

```

## C4 Component Diagram - CLI Application

This C4 component diagram depicts the main components that make up the CLI application. This app is built in Python
using [click](https://github.com/pallets/click/). The application provides a small set of commands to interact with
some Jira resources, e.g. comments and issues, and can be used for debugging some interactions with your Jira instance,
e.g. to retrieve the metadata required to create/update work items.

```{mermaid}
C4Component
    title CLI Application - C4 Component Diagram

    Person(user, "Developer/User", "Interacts with Jira through terminal")

    Container(controller, "API Controller", "Python", "Provides core functionality for managing JIra resources")
    Container(api, "API", "Python", "Provides access to Jira")

    Container_Boundary(cli, "CLI Application") {
        Component(command_handler, "Command Handler", "Python")
        Component(command_manager, "CLI Command Manager", "Python")
        Component(jira_issue_comment_renderer, "JiraIssueCommentRenderer", "Python")
        Component(jira_issue_comments_renderer, "JiraIssueCommentsRenderer", "Python")
        Component(jira_issue_comment_text_renderer, "JiraIssueCommentTextRenderer", "Python")
        Component(jira_issue_metadata_renderer, "JiraIssueMetadataRenderer", "Python")
        Component(jira_issue_search_renderer, "JiraIssueSearchRenderer", "Python")
        Component(jira_issue_group_renderer, "JiraUserGroupRenderer", "Python")
        Component(jira_issue_user_renderer, "JiraUserRenderer", "Python")
        Component(themes_renderer, "ThemesRenderer", "Python")

        Rel(command_handler, controller, "Uses", "")
        Rel(command_manager, jira_issue_comment_renderer, "Uses", "")
        Rel(command_manager, jira_issue_comments_renderer, "Uses", "")
        Rel(command_manager, jira_issue_comment_text_renderer, "Uses", "")
        Rel(command_manager, jira_issue_metadata_renderer, "Uses", "")
        Rel(command_manager, jira_issue_search_renderer, "Uses", "")
        Rel(command_manager, jira_issue_group_renderer, "Uses", "")
        Rel(command_manager, jira_issue_user_renderer, "Uses", "")
        Rel(command_manager, themes_renderer, "Uses", "")
    }

    System_Ext(jira_api, "Atlassian Jira API", "REST API for accessing Jira Cloud/Data Center")

    Rel(user, command_manager, "Uses", "")
    Rel(command_manager, command_handler, "Uses", "")
    Rel(controller, api, "Uses", "")
    Rel(api, jira_api, "Uses", "")

```

## C4 Component Diagram - UI Application

This C4 component diagram depicts the main components that make up the UI application. The app is built in Python
using the [Texualize's Textual Framework](https://textual.textualize.io/), [Rich](https://github.com/textualize/rich)
and [Python's asyncio](https://docs.python.org/3/library/asyncio.html) framework, among other components. The
application provides a UI that allows users to interact with Jira via a number of use cases.

```{mermaid}
C4Component
    title UI Application - C4 Component Diagram

    Person(user, "Developer/User", "Interacts with Jira through terminal")

    Container(controller, "API Controller", "Python", "Provides core functionality for managing JIra resources")
    Container(api, "API", "Python", "Provides access to Jira")

    Container_Boundary(ui, "UI Application") {
        Component(main_screen, "Main Screen", "Textual Widget")

        Component(project_selection_input, "Project Selection Input", "Textual Widget")
        Component(issuetypeselectioninput, "Project Selection Input", "Textual Widget")
        Component(issuestatusselectioninput, "Issue Status Selection Input", "Textual Widget")
        Component(jirauserinput, "User Input", "Textual Widget")
        Component(searchresultscontainer, "Search Results Container", "Textual Widget")
        Component(workiteminfocontainer, "Work Item Info Container", "Textual Widget")
        Component(issuecommentswidget, "Issue Comments Widget", "Textual Widget")
        Component(relatedissueswidget, "Related Issues Widget", "Textual Widget")
        Component(issueattachmentswidget, "Issue Attachments Widget", "Textual Widget")
        Component(issueremotelinkswidget, "Issue Remote Links Widget", "Textual Widget")
        Component(issuechildworkitemswidget, "Issue Child Work Items Widget", "Textual Widget")
        Component(issue_details_widget, "Issue Details Widget", "Textual Widget")

        Rel(main_screen, project_selection_input, "Uses", "")
        Rel(main_screen, issuetypeselectioninput, "Uses", "")
        Rel(main_screen, issuestatusselectioninput, "Uses", "")
        Rel(main_screen, jirauserinput, "Uses", "")
        Rel(main_screen, searchresultscontainer, "Uses", "")
        Rel(main_screen, workiteminfocontainer, "Uses", "")
        Rel(main_screen, issuechildworkitemswidget, "Uses", "")
        Rel(main_screen, issueremotelinkswidget, "Uses", "")
        Rel(main_screen, issueattachmentswidget, "Uses", "")
        Rel(main_screen, relatedissueswidget, "Uses", "")
        Rel(main_screen, issuecommentswidget, "Uses", "")

        Rel(main_screen, issue_details_widget, "Uses", "")
    }

    System_Ext(jira_api, "Atlassian Jira API", "REST API for accessing Jira Cloud/Data Center")

    Rel(user, main_screen, "Uses", "")
    Rel(controller, api, "Uses", "")
    Rel(api, jira_api, "Uses", "")
    Rel(main_screen, controller, "Uses", "")
```

## UML Class Diagrams

### JiraTUI UI Application

````{toggle}
```{mermaid}
    ---
    title: Key classes that make up the JiraTUI's UI application.
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        JiraApp *-- QuitScreen
        JiraApp *-- MainScreen
        JiraApp *-- ServerInfoScreen
        JiraApp *-- ConfigFileScreen
        JiraApp --> JiraServerInfo
        namespace jiratui.widgets {
            class MainScreen
        }
        namespace jiratui.widgets.screens {
            class QuitScreen
            class ConfigFileScreen
        }
        namespace jiratui.widgets.screens {
            class ServerInfoScreen
        }
        namespace jiratui.models {
            class JiraServerInfo
        }
```
````

### UI's Main Screen

````{toggle}
```{mermaid}
    ---
    title: Key classes that make up the MainScreen class.
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        direction LR
        %% Textual Framework Classes
        namespace textual {
            class Screen {
                <<textual.screen>>
            }

            class Container {
                <<textual.containers>>
            }

            class Horizontal {
                <<textual.containers>>
            }

            class HorizontalGroup {
                <<textual.containers>>
            }

            class ItemGrid {
                <<textual.containers>>
            }

            class Vertical {
                <<textual.containers>>
            }

            class Widget {
                <<textual.widgets>>
            }

            class Button {
                <<textual.widgets>>
            }

            class Footer {
                <<textual.widgets>>
            }

            class Header {
                <<textual.widgets>>
            }

            class TabbedContent {
                <<textual.widgets>>
            }

            class TabPane {
                <<textual.widgets>>
            }

            class Worker {
                <<textual.worker>>
            }
        }

        %% MainScreen Class
        class MainScreen {
            <<jiratui.widgets.screen>>
        }

        %% JiraUI Widgets
        namespace jiratui.widgets.filters {
            class ProjectSelectionInput {
                <<jiratui.widgets.filters>>
            }

            class IssueTypeSelectionInput {
                <<jiratui.widgets.filters>>
            }

            class IssueStatusSelectionInput {
                <<jiratui.widgets.filters>>
            }

            class WorkItemInputWidget {
                <<jiratui.widgets.filters>>
            }

            class IssueSearchCreatedFromWidget {
                <<jiratui.widgets.filters>>
            }

            class IssueSearchCreatedUntilWidget {
                <<jiratui.widgets.filters>>
            }

            class OrderByWidget {
                <<jiratui.widgets.filters>>
            }

            class ActiveSprintCheckbox {
                <<jiratui.widgets.filters>>
            }

            class JQLSearchWidget {
                <<jiratui.widgets.filters>>
            }
        }

        namespace jiratui.widgets.commons.users {
            class JiraUserInput {
                <<jiratui.widgets.commons.users>>
            }

            class UsersAutoComplete {
                <<jiratui.widgets.commons.users>>
            }
        }

        namespace jiratui.widgets.search {
            class DataTableSearchInput {
                <<jiratui.widgets.search>>
            }

            class IssuesSearchResultsTable {
                <<jiratui.widgets.search>>
            }

            class SearchResultsContainer {
                <<jiratui.widgets.search>>
            }
        }

        class WorkItemInfoContainer {
            <<jiratui.widgets.work_item_info.info>>
        }

        class IssueDetailsWidget {
            <<jiratui.widgets.work_item_details.details>>
        }

        class IssueCommentsWidget {
            <<jiratui.widgets.comments.comments>>
        }

        class RelatedIssuesWidget {
            <<jiratui.widgets.related_work_items.related_issues>>
        }

        class IssueRemoteLinksWidget {
            <<jiratui.widgets.remote_links.links>>
        }

        class IssueChildWorkItemsWidget {
            <<jiratui.widgets.work_item_subtasks>>
        }

        class IssueAttachmentsWidget {
            <<jiratui.widgets.attachments.attachments>>
        }

        namespace jiratui.api_controller.controller {
            class APIController {
                <<jiratui.api_controller.controller>>
            }

            class APIControllerResponse {
                <<jiratui.api_controller.controller>>
            }
        }

        %% Inheritance relationships
        MainScreen --|> Screen

        %% Composition and Usage relationships
        MainScreen --> APIController : uses
        MainScreen --> ProjectSelectionInput : contains
        MainScreen --> IssueTypeSelectionInput : contains
        MainScreen --> IssueStatusSelectionInput : contains
        MainScreen --> JiraUserInput : contains
        MainScreen --> WorkItemInputWidget : contains
        MainScreen --> IssueSearchCreatedFromWidget : contains
        MainScreen --> IssueSearchCreatedUntilWidget : contains
        MainScreen --> OrderByWidget : contains
        MainScreen --> ActiveSprintCheckbox : contains
        MainScreen --> JQLSearchWidget : contains
        MainScreen --> Button : contains
        MainScreen --> Header : contains
        MainScreen --> Footer : contains
        MainScreen --> Horizontal : contains
        MainScreen --> HorizontalGroup : contains
        MainScreen --> ItemGrid : contains
        MainScreen --> Vertical : contains
        MainScreen --> TabbedContent : contains
        MainScreen --> TabPane : contains
        MainScreen --> DataTableSearchInput : contains
        MainScreen --> IssuesSearchResultsTable : contains
        MainScreen --> SearchResultsContainer : contains
        MainScreen --> WorkItemInfoContainer : contains
        MainScreen --> IssueDetailsWidget : contains
        MainScreen --> IssueCommentsWidget : contains
        MainScreen --> RelatedIssuesWidget : contains
        MainScreen --> IssueRemoteLinksWidget : contains
        MainScreen --> IssueChildWorkItemsWidget : contains
        MainScreen --> IssueAttachmentsWidget : contains
        MainScreen --> UsersAutoComplete : mounts
        MainScreen --> APIControllerResponse : uses
        MainScreen --> Worker : uses
    ```
````

### Common Widgets

````{toggle}
```{mermaid}
    ---
    title: Classes for Common Widgets.
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        %% Textual Framework Base Classes
        class Input {
            <<textual.widgets>>
        }

        class MaskedInput {
            <<textual.widgets>>
        }

        class Select {
            <<textual.widgets>>
        }

        class SelectionList {
            <<textual.widgets>>
        }

        class TextArea {
            <<textual.widgets>>
        }

        class DateInput {
            <<jiratui.widgets.base>>
        }

        %% Base Field Classes
        class BaseFieldWidget {
            <<jiratui.widgets.commons.base>>
            +mode: FieldMode
            +field_id: str
            +jira_field_key: str
        }

        class BaseUpdateFieldWidget {
            <<jiratui.widgets.commons.base>>
            +original_value: Any
        }

        class FieldMode {
            <<jiratui.widgets.commons.base>>
            CREATE
            UPDATE
        }

        %% Date and DateTime Widgets
        class DateInputWidget {
            +mode: FieldMode
            +original_value: str | None
            +field_supports_update: bool
            +get_value_for_update() str | None
            +value_has_changed: bool
        }

        class DateTimeInputWidget {
            +mode: FieldMode
            +original_value: str | None
            +field_supports_update: bool
            +get_value_for_update() str | None
            +value_has_changed: bool
        }

        %% Text and String Widgets
        class TextInputWidget {
            +mode: FieldMode
            +original_value: str | None
            +field_supports_update: bool
            +get_value_for_update() str
            +value_has_changed: bool
        }

        class LabelsWidget {
            +mode: FieldMode
            +original_value: list[str]
            +supports_update: bool
            +get_value_for_create() list[str]
            +get_value_for_update() list[str]
            +value_has_changed: bool
        }

        class URLWidget {
            +mode: FieldMode
            +original_value: str | None
            +field_supports_update: bool
            +get_value_for_create() str | None
            +get_value_for_update() str | None
            +value_has_changed: bool
        }

        class NumericInputWidget {
            +mode: FieldMode
            +original_value: str | int | float | None
            +field_supports_update: bool
            +get_value_for_create() int | float | None
            +get_value_for_update() int | float | None
            +value_has_changed: bool
        }

        class SingleUserPickerWidget {
            +mode: FieldMode
            +field_id: str
            +jira_field_key: str
            +original_value: dict | None
            +update_enabled: bool
            +account_id: str | None
            +set_value(account_id, name) None
            +get_value_for_create() dict | None
            +get_value_for_update() dict | None
            +value_has_changed: bool
            +clear() None
        }

        %% Selection and Multi-Select Widgets
        class SelectionWidget {
            +mode: FieldMode
            +original_value: str | None
            +field_supports_update: bool
            +get_value_for_create() str | None
            +get_value_for_update() str | None
            +value_has_changed: bool
        }

        class MultiSelectWidget {
            +mode: FieldMode
            +original_value: list[str]
            +field_supports_update: bool
            +get_value_for_create() list[str]
            +get_value_for_update() list[str]
            +value_has_changed: bool
        }

        %% TextArea-based Widgets
        class DescriptionWidget {
            +mode: FieldMode
            +original_value: str | None
            +field_supports_update: bool
            +get_value_for_create() str | None
            +get_value_for_update() str | None
            +value_has_changed: bool
        }

        class PlainTextTextAreaWidget {
            +mode: FieldMode
            +original_value: str | None
            +field_supports_update: bool
            +get_value_for_create() str | None
            +get_value_for_update() str | None
            +value_has_changed: bool
        }

        class ReadOnlyTextAreaWidget {
            +mode: FieldMode
            +content: str
        }

        %% Specialized Widgets
        class SprintWidget {
            +mode: FieldMode
            +original_value: str | None
            +field_supports_update: bool
            +get_value_for_create() str | None
            +get_value_for_update() str | None
            +value_has_changed: bool
        }

        class EpicLinkWidget {
            +mode: FieldMode
            +original_value: str | None
            +field_supports_update: bool
            +get_value_for_create() str | None
            +get_value_for_update() str | None
            +value_has_changed: bool
        }

        class MultiUserPickerWidget {
            +mode: FieldMode
            +original_value: list[dict]
            +field_supports_update: bool
            +get_value_for_create() list[dict]
            +get_value_for_update() list[dict]
            +value_has_changed: bool
        }

        class MultiIssuePickerWidget {
            +mode: FieldMode
            +original_value: list[str]
            +field_supports_update: bool
            +get_value_for_create() list[str]
            +get_value_for_update() list[str]
            +value_has_changed: bool
        }

        %% Inheritance relationships
        DateInputWidget --|> DateInput
        DateInputWidget --|> BaseFieldWidget
        DateInputWidget --|> BaseUpdateFieldWidget

        DateTimeInputWidget --|> MaskedInput
        DateTimeInputWidget --|> BaseFieldWidget
        DateTimeInputWidget --|> BaseUpdateFieldWidget

        TextInputWidget --|> Input
        TextInputWidget --|> BaseFieldWidget
        TextInputWidget --|> BaseUpdateFieldWidget

        LabelsWidget --|> Input
        LabelsWidget --|> BaseFieldWidget
        LabelsWidget --|> BaseUpdateFieldWidget

        URLWidget --|> Input
        URLWidget --|> BaseFieldWidget
        URLWidget --|> BaseUpdateFieldWidget

        NumericInputWidget --|> Input
        NumericInputWidget --|> BaseFieldWidget
        NumericInputWidget --|> BaseUpdateFieldWidget

        SingleUserPickerWidget --|> Input

        SelectionWidget --|> Select
        SelectionWidget --|> BaseFieldWidget
        SelectionWidget --|> BaseUpdateFieldWidget

        MultiSelectWidget --|> SelectionList
        MultiSelectWidget --|> BaseFieldWidget
        MultiSelectWidget --|> BaseUpdateFieldWidget

        DescriptionWidget --|> TextArea
        DescriptionWidget --|> BaseFieldWidget
        DescriptionWidget --|> BaseUpdateFieldWidget

        PlainTextTextAreaWidget --|> TextArea
        PlainTextTextAreaWidget --|> BaseFieldWidget
        PlainTextTextAreaWidget --|> BaseUpdateFieldWidget

        ReadOnlyTextAreaWidget --|> TextArea

        SprintWidget --|> Input
        SprintWidget --|> BaseFieldWidget
        SprintWidget --|> BaseUpdateFieldWidget

        EpicLinkWidget --|> Input
        EpicLinkWidget --|> BaseFieldWidget
        EpicLinkWidget --|> BaseUpdateFieldWidget

        MultiUserPickerWidget --|> Input
        MultiUserPickerWidget --|> BaseFieldWidget
        MultiUserPickerWidget --|> BaseUpdateFieldWidget

        MultiIssuePickerWidget --|> Input
        MultiIssuePickerWidget --|> BaseFieldWidget
        MultiIssuePickerWidget --|> BaseUpdateFieldWidget
```
````

#### Base Widgets

````{toggle}
```{mermaid}
    ---
    title: Classes for Base Widgets.
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        %% Enums
        class FieldMode {
            <<enum>>
            CREATE
            UPDATE
        }

        %% Textual Framework Base Classes
        class Input {
            <<textual.widgets>>
        }

        class Select {
            <<textual.widgets>>
        }

        class AutoComplete {
            <<textual_autocomplete>>
        }

        class TargetState {
            <<textual_autocomplete>>
        }

        class DropdownItem {
            <<textual_autocomplete>>
        }

        %% External Dependencies
        class APIController {
            <<jiratui.api_controller>>
        }

        class APIControllerResponse {
            <<jiratui.api_controller>>
        }

        class JiraUser {
            <<jiratui.models>>
            +account_id: str
            +display_name: str
        }

        class JQLAutocompleteSuggestion {
            <<jiratui.models>>
            +value: str
        }

        %% Base Mixin Classes
        class BaseFieldWidget {
            <<mixin>>
            +mode: FieldMode
            +field_id: str
            +jira_field_key: str | None
            +required: bool

            +setup_base_field(mode, field_id, jira_field_key, title, required, compact) None
            +mark_required() None
        }

        class BaseUpdateFieldWidget {
            <<mixin>>
            +original_value: Any
            +value_has_changed: bool

            +setup_update_field(jira_field_key, original_value, field_supports_update) None
        }

        %% Utility Class
        class ValidationUtils {
            <<utility>>
            +is_empty_or_whitespace(value)$ bool
            +values_differ(original, current, ignore_whitespace)$ bool
        }

        %% Widget Implementations
        class ProjectSelectionWidget {}

        class IssueTypeSelectionWidget {}

        %% AutoComplete Implementations
        class LabelsAutoComplete {}

        class WorkItemKeyAutoComplete {}

        class MultiUserPickerAutoComplete {}

        class MultiIssuePickerAutoComplete {}

        %% Inheritance relationships
        ProjectSelectionWidget --|> Select
        ProjectSelectionWidget --|> BaseFieldWidget
        ProjectSelectionWidget --|> BaseUpdateFieldWidget

        IssueTypeSelectionWidget --|> Select
        IssueTypeSelectionWidget --|> BaseFieldWidget
        IssueTypeSelectionWidget --|> BaseUpdateFieldWidget

        LabelsAutoComplete --|> AutoComplete
        WorkItemKeyAutoComplete --|> AutoComplete
        MultiUserPickerAutoComplete --|> AutoComplete
        MultiIssuePickerAutoComplete --|> AutoComplete

        %% Usage relationships
        ProjectSelectionWidget --> APIController : uses
        IssueTypeSelectionWidget --> APIController : uses

        LabelsAutoComplete --> APIController : uses
        LabelsAutoComplete --> Input : attached to
        LabelsAutoComplete --> DropdownItem : creates
        LabelsAutoComplete --> TargetState : receives

        WorkItemKeyAutoComplete --> APIController : uses
        WorkItemKeyAutoComplete --> Input : attached to
        WorkItemKeyAutoComplete --> DropdownItem : creates
        WorkItemKeyAutoComplete --> TargetState : receives

        MultiUserPickerAutoComplete --> APIController : uses
        MultiUserPickerAutoComplete --> Input : attached to
        MultiUserPickerAutoComplete --> DropdownItem : creates
        MultiUserPickerAutoComplete --> JiraUser : receives
        MultiUserPickerAutoComplete --> TargetState : receives

        MultiIssuePickerAutoComplete --> APIController : uses
        MultiIssuePickerAutoComplete --> Input : attached to
        MultiIssuePickerAutoComplete --> DropdownItem : creates
        MultiIssuePickerAutoComplete --> TargetState : receives

        FieldMode --> ProjectSelectionWidget : uses
        FieldMode --> IssueTypeSelectionWidget : uses
```
````

#### Users Widgets

````{toggle}
```{mermaid}
    ---
    title: Classes for Widgets related to Users.
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        class JiraUserInput {

        }

        class UsersAutoComplete {

        }

        namespace textual_autocomplete {
            class AutoComplete {
            }

            class DropdownItem {
            }

            class TargetState {
            }
        }

        namespace textual {
            class Input {
            }

            class Reactive {
            }
        }

        namespace jiratui.api_controller.controller {
            class APIControllerResponse {
            }

            class APIController {
            }
        }

        JiraUserInput --|> Input
        UsersAutoComplete --|> AutoComplete
        UsersAutoComplete --> APIController
        UsersAutoComplete --> DropdownItem
        UsersAutoComplete --> TargetState
        UsersAutoComplete --> APIControllerResponse
        JiraUserInput --> Reactive
```
````

#### Factory Utils Module

````{toggle}
```{mermaid}
    ---
    title: Classes for bulding widgets factory utilities.
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        %% Textual Framework Base Classes
        namespace textual.widgets {
            class Widget {
                <<textual.widgets>>
            }

            class Select {
                <<textual.widgets>>
            }
        }

        %% Enums and Models
        class FieldMode {
            <<jiratui.widgets.commons>>
            CREATE
            UPDATE
        }

        %% Helper Classes
        class FieldMetadata {
            +field_id: str
            +name: str
            +key: str
            +required: bool
            +schema: dict
            +custom_type: str | None
            +schema_type: str
            +allowed_values: list~dict~
            +has_default: bool
            +default_value: dict | None
            +operations: list~str~
            +supports_update: bool
            +is_custom_field: bool

            +__init__(raw_metadata) None
        }

        class AllowedValuesParser {
            <<utility>>
            +parse_options(allowed_values)$ list~tuple~str, str~~
        }

        %% Widget Product Classes
        namespace jiratui.widgets.commons.widgets {
            class SingleUserPickerWidget {
                <<jiratui.widgets.commons.widgets>>
            }

            class NumericInputWidget {
                <<jiratui.widgets.commons.widgets>>
            }

            class SelectionWidget {
                <<jiratui.widgets.commons.widgets>>
            }

            class DateInputWidget {
                <<jiratui.widgets.commons.widgets>>
            }

            class DateTimeInputWidget {
                <<jiratui.widgets.commons.widgets>>
            }

            class TextInputWidget {
                <<jiratui.widgets.commons.widgets>>
            }

            class URLWidget {
                <<jiratui.widgets.commons.widgets>>
            }

            class LabelsWidget {
                <<jiratui.widgets.commons.widgets>>
            }

            class MultiSelectWidget {
                <<jiratui.widgets.commons.widgets>>
            }

            class ReadOnlyADFMarkdownTextAreaWidget {
                <<jiratui.widgets.commons.adf>>
            }

            class ReadOnlyPlainTextTextAreaWidget {
                <<jiratui.widgets.commons.widgets>>
            }
        }

        %% Factory Class
        class WidgetBuilder {
            <<factory>>
            +build_user_picker(mode, metadata, current_value)$ Widget
            +build_numeric(mode, metadata, current_value)$ Widget
            +build_selection(mode, metadata, options, initial_value, current_value)$ Widget
            +build_date(mode, metadata, current_value)$ Widget
            +build_datetime(mode, metadata, current_value)$ Widget
            +build_text(mode, metadata, current_value)$ Widget
            +build_url(mode, metadata, current_value)$ Widget
            +build_labels(mode, metadata, current_value)$ Widget
            +build_multicheckboxes(mode, metadata, current_value)$ Widget
            +build_read_only_rich_text_widget(jira_field_key, field_name, required, content)$ ReadOnlyADFMarkdownTextAreaWidget | ReadOnlyPlainTextTextAreaWidget
        }

        %% Usage relationships
        WidgetBuilder --> FieldMetadata : receives
        WidgetBuilder --> AllowedValuesParser : uses
        WidgetBuilder --> FieldMode : uses

        WidgetBuilder --> SingleUserPickerWidget : creates
        WidgetBuilder --> NumericInputWidget : creates
        WidgetBuilder --> SelectionWidget : creates
        WidgetBuilder --> DateInputWidget : creates
        WidgetBuilder --> DateTimeInputWidget : creates
        WidgetBuilder --> TextInputWidget : creates
        WidgetBuilder --> URLWidget : creates
        WidgetBuilder --> LabelsWidget : creates
        WidgetBuilder --> MultiSelectWidget : creates
        WidgetBuilder --> ReadOnlyADFMarkdownTextAreaWidget : creates
        WidgetBuilder --> ReadOnlyPlainTextTextAreaWidget : creates
```
````

(architecture-work-item-attachments-classes)=
### Widgets for Supporting File Attachment

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        namespace attachments.add {
            class AddAttachmentScreen
            class FileNameInputWidget {
                +__init__(): void
            }
        }

        namespace attachments.attachments {
            class WorkItemAttachments
            class AttachmentsDataTable
            class IssueAttachmentsWidget
            class ViewAttachmentScreen
            class FileAttachmentWidget {
                +build_widget(file_type, content): Widget | None
            }
        }

        namespace textual {
            class Screen
            class ModalScreen
            class DataTable
            class Input
            class VerticalScroll
            class Widget
            class Markdown
            class TextArea
            class Image
            class LoadingIndicator
            class Static
        }

        AddAttachmentScreen --|> Screen
        FileNameInputWidget --|> Input
        AttachmentsDataTable --|> DataTable
        IssueAttachmentsWidget --|> VerticalScroll
        ViewAttachmentScreen --|> ModalScreen
        FileAttachmentWidget --> Markdown: creates
        FileAttachmentWidget --> TextArea: creates
        FileAttachmentWidget --> Image: creates
        FileAttachmentWidget --> Static: creates
        ViewAttachmentScreen --> Widget: displays
        ViewAttachmentScreen --> LoadingIndicator: uses
        AddAttachmentScreen --> FileNameInputWidget: uses
        IssueAttachmentsWidget --> AttachmentsDataTable: contains
        IssueAttachmentsWidget --> WorkItemAttachments: uses
        IssueAttachmentsWidget --> AddAttachmentScreen: opens
        ViewAttachmentScreen --> FileAttachmentWidget: uses
        AttachmentsDataTable --> ViewAttachmentScreen: opens

```
````

(architecture-work-item-comments-classes)=
### Widgets for Supporting Work Item Comments

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        namespace jiratui.widgets.comments {
            class CommentCollapsible
            class IssueCommentsWidget
        }

        namespace jiratui.widgets.comments.add {
            class AddCommentScreen
        }

        namespace textual {
            class Collapsible
            class VerticalScroll
            class Screen
            class TextArea
            class Static
            class ItemGrid
        }

        Collapsible <|-- CommentCollapsible
        VerticalScroll <|-- IssueCommentsWidget
        Screen <|-- AddCommentScreen
        IssueCommentsWidget ..> CommentCollapsible: contains
        AddCommentScreen o-- TextArea
        AddCommentScreen o-- Static
        AddCommentScreen o-- ItemGrid
        IssueCommentsWidget --> AddCommentScreen: opens
```
````

(architecture-work-item-links-classes)=
### Widgets for Supporting Work Item Links

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        namespace jiratui.widgets.remote_links.add {
            class RemoteLinkURLInputWidget
            class RemoteLinkNameInputWidget
            class AddRemoteLinkScreen
        }

        namespace jiratui.widgets.remote_links.links {
            class IssueRemoteLinkCollapsible
            class IssueRemoteLinksWidget
        }

        namespace textual {
            class Input
            class Screen
            class Collapsible
            class VerticalScroll
        }

        Input <|-- RemoteLinkURLInputWidget
        Input <|-- RemoteLinkNameInputWidget
        Screen <|-- AddRemoteLinkScreen
        Collapsible <|-- IssueRemoteLinkCollapsible
        VerticalScroll <|-- IssueRemoteLinksWidget
        IssueRemoteLinksWidget o-- IssueRemoteLinkCollapsible
        AddRemoteLinkScreen *--> RemoteLinkURLInputWidget
        AddRemoteLinkScreen *--> RemoteLinkNameInputWidget
        IssueRemoteLinksWidget --> AddRemoteLinkScreen: opens

```
````

(architecture-work-item-subtasks-classes)=
### Widgets for Supporting Work Item Subtasks

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        namespace jiratui.widgets.work_item_subtasks.subtasks {
            class ChildWorkItemCollapsible
            class IssueChildWorkItemsWidget
            class CreateSubtask
        }

        namespace textual {
            class Collapsible
            class VerticalScroll
        }
        namespace jiratui.widgets.screens.work_item_quick_view {
            class WorkItemQuickViewScreen
        }

        Collapsible <|-- ChildWorkItemCollapsible
        VerticalScroll <|-- IssueChildWorkItemsWidget
        IssueChildWorkItemsWidget o-- ChildWorkItemCollapsible
        ChildWorkItemCollapsible --> WorkItemQuickViewScreen: opens
        IssueChildWorkItemsWidget o-- CreateSubtask
```
````

(architecture-related-work-items-classes)=
### Widgets for Supporting Work Item Related Issues

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        namespace related_work_items.add {
            class AddWorkItemRelationshipScreen
            class LinkedWorkItemInputWidget
            class IssueLinkTypeSelector
        }

        namespace related_work_items.related_issues {
            class RelatedIssuesWidget
            class RelatedIssueCollapsible
            class LinkDeleted {
                +link_id: str
            }
            class WorkItemRelatedItems
        }

        namespace textual {
            class Screen
            class Input
            class Select
            class Button
            class VerticalScroll
            class Collapsible
            class Link
            class Text
            class ItemGrid
            class Rule
            class Static
        }

        AddWorkItemRelationshipScreen --|> Screen
        LinkedWorkItemInputWidget --|> Input
        IssueLinkTypeSelector --|> Select
        RelatedIssuesWidget --|> VerticalScroll
        RelatedIssueCollapsible --|> Collapsible
        RelatedIssueCollapsible --> Text: uses
        RelatedIssueCollapsible --> Link: uses
        AddWorkItemRelationshipScreen --> LinkedWorkItemInputWidget: uses
        AddWorkItemRelationshipScreen --> IssueLinkTypeSelector: uses
        RelatedIssueCollapsible --> LinkDeleted: posts
        RelatedIssuesWidget --> RelatedIssueCollapsible: contains
        RelatedIssuesWidget --> WorkItemRelatedItems: contains
        RelatedIssuesWidget --> AddWorkItemRelationshipScreen: opens
        AddWorkItemRelationshipScreen o-- Button
        AddWorkItemRelationshipScreen o-- ItemGrid
        AddWorkItemRelationshipScreen o-- Rule
        AddWorkItemRelationshipScreen o-- Static
```
````

(architecture-create-work-item-classes)=
### Widgets to Support Creating Work Items

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        namespace jiratui.widgets.create_work_item {
            class AddWorkItemScreen
            class TextAreaTabPane
            class TextAreaTabbedContent
        }

        namespace jiratui.widgets.create_work_item.fields {
            class WorkItemProjectSelectionField
            class WorkItemTypeSelectionField
            class SummaryField
            class ParentKeyField
        }

        namespace textual {
            class Screen
            class TabPane
            class TabbedContent
            class Input
        }
        namespace jiratui.widgets.commons.users {
            class JiraUserInput
            class UsersAutoComplete
        }

        Screen <|-- AddWorkItemScreen
        TabPane <|-- TextAreaTabPane
        TabbedContent <|-- TextAreaTabbedContent
        Input <|-- SummaryField
        Input <|-- ParentKeyField
        AddWorkItemScreen *-- WorkItemProjectSelectionField
        AddWorkItemScreen *-- WorkItemTypeSelectionField
        AddWorkItemScreen *-- SummaryField
        AddWorkItemScreen *-- ParentKeyField
        AddWorkItemScreen *-- JiraUserInput
        AddWorkItemScreen *-- UsersAutoComplete
        AddWorkItemScreen *-- TextAreaTabbedContent
        TextAreaTabbedContent *-- TextAreaTabPane
```
````

(architecture-update-work-item-classes)=
### Widgets for Supporting Updating Work Item

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        namespace textual {
            class ItemGrid
            class Vertical
        }

        namespace jiratui.widgets.commons.widgets {
            class DateInputWidget
            class DateTimeInputWidget
            class LabelsWidget
            class MultiSelectWidget
            class MultiUserPickerWidget
            class NumericInputWidget
            class SelectionWidget
            class SingleUserPickerWidget
            class TextInputWidget
            class URLWidget
        }

        namespace jiratui.widgets.work_item_details.fields {
            class IssueDetailsPrioritySelection
            class IssueDetailsStatusSelection
            class IssueKeyField
            class IssueParentField
            class IssueSprintField
            class IssueSummaryField
            class IssueTypeField
            class ProjectIDField
            class TimeTrackingWidget
            class WorkItemDetailsDueDate
            class WorkItemFlagField
        }

        class DynamicFieldsWidgets
        class StaticFieldsWidgets
        class IssueDetailsWidget

        DynamicFieldsWidgets --|> ItemGrid
        StaticFieldsWidgets --|> ItemGrid
        IssueDetailsWidget --|> Vertical

        IssueDetailsWidget o--> IssueSummaryField
        IssueDetailsWidget o--> IssueDetailsPrioritySelection
        IssueDetailsWidget o--> IssueDetailsStatusSelection
        IssueDetailsWidget o--> IssueKeyField
        IssueDetailsWidget o--> IssueParentField
        IssueDetailsWidget o--> IssueSprintField
        IssueDetailsWidget o--> IssueTypeField
        IssueDetailsWidget o--> ProjectIDField
        IssueDetailsWidget o--> WorkItemDetailsDueDate
        IssueDetailsWidget --> TimeTrackingWidget: contains
        IssueDetailsWidget --> WorkItemFlagField: contains
        IssueDetailsWidget --> DynamicFieldsWidgets: contains
        IssueDetailsWidget --> StaticFieldsWidgets: contains
        IssueDetailsWidget --> NumericInputWidget: contains

        IssueDetailsWidget --> DateInputWidget: contains
        IssueDetailsWidget --> DateTimeInputWidget: contains
        IssueDetailsWidget --> SelectionWidget: contains
        IssueDetailsWidget --> URLWidget: contains
        IssueDetailsWidget --> MultiSelectWidget: contains
        IssueDetailsWidget --> TextInputWidget: contains
        IssueDetailsWidget --> LabelsWidget: contains
        IssueDetailsWidget --> MultiUserPickerWidget: contains
        IssueDetailsWidget --> SingleUserPickerWidget: contains
```
````

(architecture-worklogs)=
### Widgets for Supporting Managing Work Logs

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        namespace textual {
            class Horizontal
            class Vertical
            class VerticalScroll
            class Footer
        }
        namespace work_item_worklog.widgets {
            class TimeTrackingWidget
            class TimeSpentInput
            class TimeRemainingInput
            class LogDateTimeInput
            class WorkDescription
        }

        namespace work_item_worklog.screens {
            class WorkItemWorkLogScreen
            class WorkLogCollapsible
            class LogWorkScreen
        }

        WorkItemWorkLogScreen o--> Vertical
        WorkItemWorkLogScreen o--> VerticalScroll
        WorkItemWorkLogScreen o--> Horizontal
        WorkItemWorkLogScreen o--> Footer
        WorkItemWorkLogScreen o--> TimeTrackingWidget
        WorkItemWorkLogScreen "1" o--> "0..n" WorkLogCollapsible

        WorkItemWorkLogScreen --> LogWorkScreen: opens

        LogWorkScreen o--> TimeSpentInput
        LogWorkScreen o--> TimeRemainingInput
        LogWorkScreen o--> LogDateTimeInput
        LogWorkScreen o--> WorkDescription
```
````

(architecture-goto-screen)=
### Widgets for Supporting Go-To (Related Items) Screen

````{toggle}
```{mermaid}
    ---
    config:
        theme: "default"
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        namespace textual {
            class Rule
            class Static
            class VerticalScroll
            class Footer
        }

        namespace widgets.screens.goto {
            class GotToScreen
            class GoToItemsTable
        }

        GotToScreen o--> Static
        GotToScreen o--> VerticalScroll
        GotToScreen o--> Rule
        GotToScreen o--> Footer
        GotToScreen "1" o--> "1..4" GoToItemsTable
```
````
