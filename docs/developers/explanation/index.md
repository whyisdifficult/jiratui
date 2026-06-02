(concepts)=
# Concepts

This section covers the core concepts you'll need to know when contributing to JiraTUI. Rather than a how-to guide,
think of it as background knowledge that'll make it easier to understand why things are organized the way they are and
where to make changes.

When you're adding features or debugging, it helps to know how the codebase is laid out, what's driving the UI design,
how we're talking to Jira, and what tools and libraries we're using to build the interface. You'll probably find yourself
coming back here as questions pop up during development.

We've broken this down into:

- [UI and CLI Applications](cli-and-ui.md): Introduces the 2 applications provided by JiraTUI.
- [Architecture](architecture.md): How the app is structured and how the pieces fit together.
- [Jira APIs](jira-api.md): Which Jira endpoints we use and what data we're working with.
- [UI Design and Components](components.md): The building blocks we use to put the interface together.
- [Use Cases](use-cases.md): An overview of the different use cases supported by the application.

You don't need to memorize all of this before you start coding, but having these explanations handy will save you time
and help your code fit better with the rest of the project.

```{toctree}
:maxdepth: 1
cli-and-ui.md
architecture.md
jira-api.md
textual-framework.md
components.md
use-cases.md
```
