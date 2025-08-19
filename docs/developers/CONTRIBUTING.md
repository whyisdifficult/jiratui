# Contributing Guidelines

## 1. **Introduction**
Thank you for considering contributing to our project! We welcome contributions from everyone. By participating in this
project, you agree to abide by our code of conduct.

## 2. **Code of Conduct**
Please read our [Code of Conduct](CODE_OF_CONDUCT) to understand the expectations for behavior in our community.

## 3. **How to Contribute**

Here are the steps to contribute to the project:

- **Clone the Repo**: Clone the repository to your local machine using:

```bash
git clone https://github.com/whyisdifficult/jiratui.git
```

- **Set up the local environment**

```shell
cd jiratui
source .venv/bin/activate
make env  # or: uv sync --all-groups
make install_pre_commit_hooks
```

- **Create a Branch**: Create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
```

Make sure the branch's name starts with `feature/`.

- **Make Changes**: Implement your changes. Ensure that your code adheres to the project's coding style and conventions.

- **Write Tests**: If applicable, write tests for your changes to ensure they work as expected.

- **Commit Your Changes**: Commit your changes with a clear and descriptive message:
  ```bash
  git commit -m "Add feature: your-feature-name"
  ```

- **Push Your Changes**: Push your changes to the repository:

```bash
git push origin feature/your-feature-name
```

- **Create a Pull Request**: Go to the original repository and click on "New Pull Request." Select your branch and
submit the pull request. Provide a clear description of your changes and why they are needed.

## 4. **Pull Request Guidelines**

When submitting a pull request, please ensure that:
- Your code is well-documented.
- You have added tests for any new features or bug fixes.
- Your changes do not break existing functionality.
- You have followed the project's coding style.

## 5. **Issue Reporting**

If you find a bug or have a feature request, please open an issue in the repository. Provide as much detail as
possible, including:

- A clear description of the issue.
- Steps to reproduce the issue.
- Any relevant screenshots or error messages.

## 6. **Code Style**

Please adhere to the following coding standards:

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
- Use meaningful variable and function names.
- Write docstrings for all public modules, functions, and classes.
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings).

## 7. **License**

By contributing to this project, you agree that your contributions will be licensed under the project's license. Please
review the [LICENSE](LICENSE) file for more details.

## 8. **Thank You!**

We appreciate your interest in contributing to our project. Your contributions help make this project better for
everyone!
