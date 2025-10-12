from git import Head, NoSuchPathError, Repo
from textual.app import ComposeResult
from textual.containers import Center, Right, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Rule, Select, Static

from jiratui.config import CONFIGURATION


class GitRepositorySelectionWidget(Select):
    """A `textual.widgets.Select` widget to display the list of available Git repositories."""

    def __init__(self, options: list):
        super().__init__(
            options=options,
            prompt='Select the repository to create the branch',
            type_to_search=True,
            compact=True,
        )
        self.valid_empty = False
        self.border_title = 'Repository'
        self.border_subtitle = '(*)'


class GitBranchNameInput(Input):
    """A `textual.widgets.Input` widget to provide the name of the branch that the user wants to create."""

    def __init__(self, value: str):
        super().__init__(value=value, placeholder='Type in the name of the branch')
        self.border_title = 'Branch Name'
        self.valid_empty = False
        self.border_subtitle = '(*)'


class GitScreen(ModalScreen[bool]):
    """A modal screen that allows the user to create a new Git branch on a target repository."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Screen')]

    def __init__(self, work_item_key: str):
        super().__init__()
        self._work_item_key = work_item_key
        self._repositories = []
        if git_repositories := CONFIGURATION.get().git_repositories:
            self._repositories = [
                (repo.get('name'), repo.get('path')) for _, repo in git_repositories.items()
            ]

    @property
    def create_branch_button(self) -> Button:
        return self.query_one('#button-create-git-branch', expect_type=Button)

    @property
    def repository_selector(self) -> GitRepositorySelectionWidget:
        return self.query_one(GitRepositorySelectionWidget)

    @property
    def branch_input(self) -> GitBranchNameInput:
        return self.query_one(GitBranchNameInput)

    @property
    def label_input(self) -> Label:
        return self.query_one('#target-repo-message', expect_type=Label)

    @property
    def checkbox_input(self) -> Checkbox:
        return self.query_one(Checkbox)

    @property
    def error_message_widget(self) -> Static:
        return self.query_one('#error-message', expect_type=Static)

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = 'Create Git Branch'
        with vertical:
            yield GitRepositorySelectionWidget(self._repositories)
            with Right():
                yield Label('', id='target-repo-message')
            yield GitBranchNameInput(value=f'feature/{self._work_item_key}')
            yield Checkbox(label='Checkout the branch after creation', value=False, compact=True)
            yield Rule()
            with Center():
                yield Button(
                    'Create',
                    variant='primary',
                    id='button-create-git-branch',
                    flat=True,
                    disabled=True,
                )
            yield Static('', id='error-message')

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.value and event.value.strip():
            self.branch_input.value = event.value.strip()
        self.create_branch_button.disabled = not (
            self.repository_selector.selection and self.branch_input.value
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        if self.repository_selector.selection:
            self.label_input.content = f'Target Repository: {self.repository_selector.selection}'
        else:
            self.label_input.content = ''
        self.create_branch_button.disabled = not (
            self.repository_selector.selection and self.branch_input.value
        )

    def _get_git_repository(self, repository_path: str) -> Repo | None:
        try:
            return Repo(repository_path)
        except NoSuchPathError:
            self.error_message_widget.content = f'Unable to find a git repository at the specified location. Check the configuration of the repo in the config file and make sure it points to the directory where the .git directory is located: {self.repository_selector.selection}'
        except Exception as e:
            self.error_message_widget.content = str(e)
        return None

    def _create_branch(self, repo: Repo, name: str) -> Head | None:
        try:
            return repo.create_head(name)
        except Exception as e:
            self.error_message_widget.content = str(e)
            return None

    @staticmethod
    def _get_repo_branches(repo: Repo) -> set[str]:
        return {branch.name.lower() for branch in repo.branches}

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'button-create-git-branch':
            if repo := self._get_git_repository(self.repository_selector.selection):
                # check that the branch we want to create does not exist
                if self.branch_input.value.lower() in self._get_repo_branches(repo):
                    self.error_message_widget.content = (
                        'The branch you want to create already exists'
                    )
                else:
                    if new_branch_reference := self._create_branch(repo, self.branch_input.value):
                        if self.checkbox_input.value is True:
                            new_branch_reference.checkout()
                            self.notify(
                                f'Branch {new_branch_reference} created and checked out successfully',
                                title='Git Integration',
                            )
                        else:
                            self.notify(
                                f'Branch {new_branch_reference} created successfully',
                                title='Git Integration',
                            )
                        self.dismiss(True)
