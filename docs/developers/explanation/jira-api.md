(jira-api)=

# Jira REST API

JiraTUI supports three REST API versions:

| API                                                                                              | Use Case                        | Key Notes                                                                                                                                             |
|--------------------------------------------------------------------------------------------------|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Jira Cloud Platform API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/) | Jira Cloud (primary)            | Supports [Atlassian Document Format (ADF)](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/); latest & actively developed |
| [Jira Cloud Platform API v2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro/) | Jira Cloud (legacy)             | Same endpoints as v3, no ADF support                                                                                                                  |
| [Data Center v7.6.1](https://docs.atlassian.com/software/jira/docs/api/REST/7.6.1/)              | Jira on-premises (aka. Jira DC) | Different endpoint set; Atlassian is deprecating DC. See below.                                                                                       |


## Cloud Platform v2 vs v3

Both versions expose the same operations. Use v3 as it adds ADF support for richer text formatting in issue descriptions
and comments.

## Data Center Support

DC testing requires an on-premises installation (see [Testing](#testing) for workarounds). The DC API differs significantly from Cloud in both endpoints and available operations.

```{Important}
Atlassian is [deprecating Data Center products](https://www.atlassian.com/blog/announcements/atlassian-ascend),
including the REST API. Development priority is Cloud Platform. DC bug fixes are supported on a limited basis.
```

## Implementation Guidelines

When adding features or fixing bugs:

- **Use only documented, officially supported endpoints**. Check [Atlassian's developer docs](https://developer.atlassian.com/cloud/jira/platform/).
- **Don't reverse-engineer the UI**. Jira's UI uses internal APIs not designed for external consumption. Stick to public APIs.
- Stuck? Ask the [Atlassian Community](https://community.atlassian.com/forums/Jira/).
