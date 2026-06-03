(writing-documentation)=
# Writing Documentation

## Framework

We follow the [Diataxis framework](https://diataxis.fr/) for organizing and writing technical documentation. If you're
new to it, take some time to familiarize yourself with the four documentation types it defines: tutorials, how-to
guides, explanations, and reference material. Each serves a different purpose and audience need. Understanding these
distinctions helps us write clearer, more useful docs.

We keep documentation as close to the code as possible using a documentation-as-code approach. This means docs live
alongside the source code, get versioned with it, and go through the same review process as everything else. A few
reasons we do this:

- Docs stay in sync with code. When you refactor, you update the docs in the same PR. No outdated information
lingering in a separate wiki somewhere.
- Lower friction. Contributing to docs is as simple as editing a Markdown file. No special tools or permissions needed.
- Searchable and discoverable. Docs are part of the repo; they show up in searches and are easy to navigate alongside
the actual implementation.
- Review and quality. Documentation changes go through code review just like everything else, keeping quality
consistent.

When you add or update features in the code, make sure to keep the relevant [UML diagrams](/developers/explanation/architecture) ,
[use cases](/developers/explanation/use-cases), and [architecture](/developers/explanation/architecture)
documentation in sync. Treat these as living artifacts that reflect the current state of the system. Outdated diagrams
are worse than no diagrams.

When you write or update docs, think about which Diataxis type you're creating, write for the intended audience, and
keep it practical and clear.

## Generate Docs Locally

We use [sphinx](https://www.sphinx-doc.org/en/master/) and the [myst-parse](https://myst-parser.readthedocs.io/en/latest/).

The Sphinx configuration file is located under the `docs` directory.

```{important}
The `docs` directory contains a symlink to `src/jiratui`. This allows us to genrate documentation with sphinx by parsing
the codebase and create documentation from Markdown syntax inside docstrings.
When you configure your IDE make sure to exclude the `docs` directory from indexing; otherwise your IDE may go nuts.
Also important, make sure to not import modules from the docs directory if you use your IDE's (or AI) suggestions.
```

If you want to generate the documentation locally to test follow these steps:

1. `make env`
2. `make docs-html`

You can then open the HTML files under `{WORK_DIRECTORY}/docs/_build/`
