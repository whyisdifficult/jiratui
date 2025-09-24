# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Bug Fixes

- Fix handling of the argument `ui --jql-expression-id` because it was not picking up the given expression id. Reported
in https://github.com/whyisdifficult/jiratui/issues/69

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
