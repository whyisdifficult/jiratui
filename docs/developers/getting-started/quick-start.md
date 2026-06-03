# Quick Start

The following steps will guide through the process of setting up your local Python environment to work on your first
contribution to the project.

**Pre-requisites**

- The project uses [Astral's uv](https://docs.astral.sh/uv/) to manage its dependencies. Follow the instructions on
their website to install.
- Make sure your Python version is supported. Refer to the `pyproject.toml` file for details.
- Make sure to read the [code style guidelines](code-style-guidelines)
- Make sure to read the [pull request guidelines](pull-request-guidelines)

**Step 1**. **Fork the Repository**

**Step 2**. **Clone the Repo**: Clone the repository to your local machine using:

```bash
git clone https://github.com/yourusername/repo.git
```

**Step 3**. **Set up the local environment**

```shell
cd <to-your-local-repo>
source .venv/bin/activate
make env  # or: uv sync --all-groups
make install_pre_commit_hooks
```

**Step 4**. **Create a Branch**: Create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
```

**Step 5**. **Make Changes**: Implement your changes. Ensure that your code adheres to the project's coding style and conventions.

**Step 6**. **Write Tests**: If applicable, write tests for your changes to ensure they work as expected.

**Step 7**. **Test your Changes**:

  - Make sure to run the tests with `make test`. See [Testing](#testing) for details.
  - To test your changes manually it's recommended to run the [Textual dev console](https://textual.textualize.io/guide/devtools/#console)

```shell
# console 1
textual console
```

```bash
# console 2
JIRA_TUI_CONFIG_FILE=path/to/config.yaml textual run --dev src/jiratui/cli.py ui
```

or,

```bash
# console 2
JIRA_TUI_CONFIG_FILE=path/to/config.yaml textual run --dev src/jiratui/app.py
```

This will allow you to test the application and see live logs in the other terminal console.

```{important}
If you make changes to the documentation then you can generate the docs locally to test your changes. You do that by
running:

`make make-docs`

For more detail shead over to [Writing Documentation](#writing-documentation).
```

**Step 8**. **Update the CHANGELOG**: make sure to update the [CHANGELOG](https://github.com/whyisdifficult/jiratui/blob/main/CHANGELOG.md)
to record the changes.

**Step 9**. **Commit Your Changes**: Commit your changes with a clear and descriptive message:

```bash
git commit -m "Add feature: your-feature-name"
```

**Step 10**. **Push Your Changes**: Push your changes to the repository:

```bash
git push origin feature/your-feature-name
```

**Step 11**. **Create a Pull Request**: After pushing, go to your forked repository on GitHub, and you will see a
prompt to create a pull request. Click on "Compare & pull request," add a description of your changes, and submit the PR.

Great! now you know the basics of how to set up your local environment to start contributing to the project.

The next step is to familiarize yourself with the [basic concepts](#concepts) of the application, including the
[use cases](#use-cases) supported by the application, [the architecture](#architecture) that supports these use cases,
the different UI components and the [Jira API implementation](#jira-api).
