# Codebase Structure

```{mermaid}
treeView-beta
    "docs"
    "jtsite"
    "src"
        "jiratui"
            "api"
            "api_controller"
            "commands"
            "css"
            "utils"
            "widgets"
                "attachments"
                "comments"
                "commons"
                "create_work_item"
                "related_work_items"
                "remote_links"
                "work_item_details"
                "work_item_info"
```



| Module                                                                                             | Description |
|----------------------------------------------------------------------------------------------------|-------------|
| [api](https://github.com/whyisdifficult/jiratui/tree/main/src/jiratui/api)                         | the module that contains the Jira API implementation classes and functionality. |
| [api_controller](https://github.com/whyisdifficult/jiratui/tree/main/src/jiratui/api_controller)   | the classes and functionality related to the API controller. |
| [widgets](https://github.com/whyisdifficult/jiratui/tree/main/src/jiratui/widgets)                 | this module contains the widgets that composed the UI of the application. Some widgets are organized further into submodules to reflect a logical relationship among them. |
| [widgets.commons](https://github.com/whyisdifficult/jiratui/tree/main/src/jiratui/widgets/commons) | a module that groups common widgets and functionality. If a widget can be reused among multiple use cases or modules consider placing the widget here. |
| [css](https://github.com/whyisdifficult/jiratui/tree/main/src/jiratui/css)                         | this module contains the .tcss file that define the CSS classes for styling the UI components. |
| [commands](https://github.com/whyisdifficult/jiratui/tree/main/src/jiratui/commands)               | the module that define handler and render classes for the CLI application. |
| [utils](https://github.com/whyisdifficult/jiratui/tree/main/src/jiratui/utils)                     | a module with common utility classes and functions. |
| [jtsite](https://github.com/whyisdifficult/jiratui/tree/main/jtsite)                         | the files of the public website served at https://jiratui.sh |
