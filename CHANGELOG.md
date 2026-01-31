# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add support for defining custom styles for work item status and type colors via the `styling` configuration key; by [@stianse](https://github.com/stianse) in https://github.com/whyisdifficult/jiratui/pull/169

## [1.6.2] - 2025-11-22

- Fix a bug when the app tries to generate the widgets for custom fields and the field doesn't have a key; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/149

## [1.6.1] - 2025-11-20

- Add a configuration variable `enable_images_support` to enable/disable image support. By default, this feature is
enabled; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/146

## [1.6.0] - 2025-11-19

### Added

- Support for Python 3.14; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/133
- Fix for flagging issues when the "flagged" field is not part of any edit screen; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/137
- Support for displaying and updating the system field `components`; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/142
- Support for displaying and updating some custom field types; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/142
  - `com.atlassian.jira.plugin.system.customfieldtypes:url`
  - `com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes`
  - `com.atlassian.jira.plugin.system.customfieldtypes:float`
  - `com.atlassian.jira.plugin.system.customfieldtypes:select`
  - `com.atlassian.jira.plugin.system.customfieldtypes:datetime`
  - `com.atlassian.jira.plugin.system.customfieldtypes:textfield`
  - `com.atlassian.jira.plugin.system.customfieldtypes:datepicker`
  - `com.atlassian.jira.plugin.system.customfieldtypes:labels`
- Support for displaying and updating some system field types; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/142
  - `date`
  - `number`
- New config variable `enable_updating_additional_fields` to enable/disable the feature that allows users to view/update
some custom fields and system fields types; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/142
- Show the parent key (if present) in the search results table; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/141

### Minor Improvements

- Upgrade `textual` and other packages (linting and tests); by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/132

## [1.5.0] - 2025-11-01

### Added

- Add support for displaying external links in ADF-based issue description; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/119
- Add support for flagging work items; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/127
- Add support for searching work items on startup; by [@vkhitrin](https://github.com/vkhitrin) in https://github.com/whyisdifficult/jiratui/pull/121
- Add support for a custom title; by [@vkhitrin](https://github.com/vkhitrin) in https://github.com/whyisdifficult/jiratui/pull/129

### Minor Improvements

- Improve searching work items on startup by waiting for workers to finish; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/123

## [1.4.0] - 2025-10-25

### Added

- Add support for time tracking; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/111
- Show Jira's global settings in the server information; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/111

### Bug Fixes

- Fix a bug that prevents searching tasks using JQL when the name of a project is "CF"; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/115
- Fix flaky tests; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/113

### Minor Improvements

- Remove the constant `APPLICATION_HELP` and replace it with a Markdown file that contains the in-app help; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/116
- Upgrade packages; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/117
    - `click` to `v8.3.0`
    - `pydantic-settings[yaml]` to `v2.11.0`
    - `python-json-logger` to `v4.0.0`
    - `textual[syntax]` to `v6.4.0`
    - `textual-dev` to `v1.8.0`

### Documentation

- Updated the documentation related to work logs; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/111

## [1.3.0] - 2025-10-14

### Added

- Enable using `^k` to copy to the clipboard the key of the issue selected/highlighted in the search results; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/92
- Enable using `^j` to copy to the clipboard the URL of the issue selected/highlighted in the search results; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/92
- Support for viewing (some) files attached to work items directly in the terminal. When the user selects an attachment
by pressing `enter` on a row, a modal screen is opened to download and display the file's content; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/99
- Support for opening attachments in the browser when the users preses `^o` on a selected/highlighted attachment; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/101
- A feature to create Git branches directly from the application's UI using the key of a work item as an initial name
for the branch. Git repositories can be configured in the config file; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/99
- [Issue-95] add support for adding comments using Jira DC; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/96

### Minor Improvements

- Improve the way we handle API exceptions and how we log them; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/89
- Upgrade `uv_build` build backend to `>=0.9.2,<0.10.0`.
- Refactor HTTP and JSON clients.
- Add hotkey `2` to focus the Info tab; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/104
- Use `python-magic` library to detect mime type when uploading files as attachments; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/105
- Update the way we display related tasks and subtasks to use border title and subtitles; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/106

### Bug Fixes

- Fix bug when adding comments using Jira DC platform. [Bug report](https://github.com/whyisdifficult/jiratui/issues/95)
- Fix sorting for search when using JQL. [Bug report](https://github.com/whyisdifficult/jiratui/issues/97) by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/100
- [Issue-93] fix bug when displaying server info for Jira DC; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/94

### Documentation

- Update the dependencies for sphinx docs; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/87

## [1.2.0] - 2025-10-04

### Added

- New feature to allow users to filter search results in the current page. The feature can be controlled via the
settings `search_results_page_filtering_enabled` and `search_results_page_filtering_minimum_term_length`.
- Use `flat` buttons for search and for confirming quitting the app.
- Refactor the logic to navigate search result pages to use dynamic actions.
- Add support for full-text search.
- Add support for client-side certificates and SSL configuration
- Add support for Bearer authentication
- Add support for configuring bearer authentication via config variable `use_bearer_authentication`.
- Add configuration variable `cloud` to distinguish between on-premises and cloud platform.
- Add an option to define the default value of the `order by` widget.

### Bug Fixes

- Fix handling of the argument `ui --jql-expression-id` because it was not picking up the given expression
id. [Bug report](https://github.com/whyisdifficult/jiratui/issues/69)

### Documentation

- Update docs to add details on how to enable/disable the search results filtering feature
- Update README and docs with instructions on how to install the tool via Homebrew.
- Update in-app documentation and official documentation with instructions on how to use the UI.

### Misc

- Upgrade `textual` to `v6.1.0`
- Add `sphinxcontrib-mermaid` to support [Mermaid](https://mermaid.js.org/) diagrams in the documentation.

## [1.1.0] - 2025-09-20

### Added

- Support for Jira API v2
- Fetch the details of an issue after updating its details; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/62
- Add support for setting the theme of the UI on start up; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/63
- Support theme configuration in the config file; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/68

### Documentation

- Update the documentation to reflect the support for Jira API v2

## [1.0.0] - 2025-09-16

### Breaking Changes

- Add support for the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/) to
make it easier to configure the application. The application will no longer use the environment variable
`JIRA_TUI_ENV_FILE`. Instead, all the configuration variables *MUST* be defined in the config file; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/52

### Added

- Use python-dateutil to parse date/times from the Jira API; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/47
- Add hot key to open an item in the browser when the item is selected/highlighted in the search results; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/48
- Documentation for AUR package; by [@trojkat](https://github.com/trojkat) in https://github.com/whyisdifficult/jiratui/pull/49
- Add support for updating the parent of a work item; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/55
- Add configuration variable to make confirming quitting optional; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/56

### Bug Fixes

- Fix bug in users selection dropdown when editing a work item by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/46


### Documentation

- Add tool logo and update installation instructions; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/51
- Update logos for the website and add logo for the read-the-docs website; by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/57

## New Contributors

- [@trojkat](https://github.com/trojkat) made their first contribution in https://github.com/whyisdifficult/jiratui/pull/49

## [0.2.0] - 2025-09-13

### Added

- Display (optional) custom fields of type text/textarea in the Info tab pane of an issue. Only custom fields that can
be edited will be displayed.
- Rename `Description` tab to `Info`.
- Add support for additional [ADF](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) node types
- Add more tests
- Show a warning in the comments of an issue when the content of the comment can not be displayed
- Add a SECURITY file with the security policy by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/11

### Changes

#### Application

- Remove dependency on [tonalite](https://github.com/Tiqets/tonalite) because it is not needed.
- Move `pre-commit` dependency to the `dev` group
- Update tests to use a mock config file
- Update `rtd` dependencies to use [sphinx-design](https://sphinx-design.readthedocs.io/en/latest/) by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/10
- Update installation command for jiratui by [@rtpg](https://github.com/rtpg) in https://github.com/whyisdifficult/jiratui/pull/25

#### Project

- Update issue templates by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/12
- Add template for requesting new features by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/13
- Update issue templates with a template for bug report by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/14
- Separate lint and tests jobs by [@whyisdifficult](https://github.com/whyisdifficult) in https://github.com/whyisdifficult/jiratui/pull/16

### New Contributors
- [@rtpg](https://github.com/rtpg) made their first contribution in https://github.com/whyisdifficult/jiratui/pull/25

## [0.1.1] - 2025-09-06

### Added

- Github workflow for publishing package to Test PyPi

### Updates

- Github workflow definitions
- License name and date
- User documentation
- Simplify pages of the main website

## [0.1.0] - 2025-09-01

### Added

- v0.1.0 First production-ready version of the tool.
