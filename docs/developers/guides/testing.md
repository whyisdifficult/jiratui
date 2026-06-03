(testing)=
# Testing

## Running Unit Tests

Run tests locally after making code changes:

```shell
# ensure the env contains the dependencies related to testing
make env
# run the tests
make test
```

## Testing Against Live Data

### Jira Cloud

The easiest option: create a free Jira Cloud account (supports up to 10 users with the
[free plan](https://www.atlassian.com/software/jira/pricing)).

Once you have your own Jira instance you can create and configure projects to tests different features.

```{Important}
Log in at least once per month to keep your account active.
```

### Jira Data Center (DC)

You have two options:

1. **Option 1**: Use your organization's instance

If your organization runs Jira DC on-premises, test directly against that instance (with appropriate permissions).

2. **Option 2**: Mock the API locally

If you don't have access to a DC instance, mock the
[Jira DC REST API](https://docs.atlassian.com/software/jira/docs/api/REST/7.6.1/) using a tool like
[WireMock](https://wiremock.org/):

- **Online**: Create a free WireMock account and generate an API mock server for the Jira DC REST API

- **Local JAR**: Run WireMock locally as a standalone JAR file

- **Docker**: Run WireMock in a [Docker container](https://wiremock.org/docs/standalone/docker/) for easier setup and
teardown

Choose whichever fits your workflow best.
