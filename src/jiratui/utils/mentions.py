"""Helpers for embedding Jira user mentions in comment Markdown.

Jira Cloud represents an ``@`` mention as an ADF ``mention`` node that carries the mentioned user's
``accountId``. The bundled ``marklas`` library already converts an HTML-like span into such a node during the
Markdown -> ADF conversion. To keep the comment editor legible, the "Add Comment" screen inserts a readable,
Markdown-link-style *token* rather than the raw span, and those tokens are expanded to spans right before the
Markdown is converted to ADF.

**Token format** (picker-generated; not intended for hand authoring)::

    @[Display Name](accountId)

is expanded to the ``marklas`` mention span::

    <span adf="mention" params='{"id":"accountId"}'>@Display Name</span>

which ``marklas.to_adf`` turns into::

    {'type': 'mention', 'attrs': {'id': 'accountId', 'text': '@Display Name'}}

Tokens that do not match the expected grammar are left untouched and are therefore submitted as literal text,
so a malformed or hand-edited token can never break comment submission.
"""

import json
import re

MENTION_TOKEN_PATTERN = re.compile(r'@\[(?P<name>[^\]]+)\]\((?P<account_id>[^)]+)\)')
"""Matches a picker-generated mention token, e.g. ``@[Homer Simpson](557058:abc-123)``."""


def build_mention_token(display_name: str, account_id: str) -> str:
    """Builds a mention token to insert into the comment editor.

    Characters that would break the token grammar (``[`` / ``]`` in the display name and ``(`` / ``)`` in the
    account id) are removed. These are exceedingly rare in Jira identities.

    Args:
        display_name: the display name of the mentioned user, e.g. ``Homer Simpson``.
        account_id: the Jira ``accountId`` of the mentioned user.

    Returns:
        A token of the form ``@[Display Name](accountId)``.
    """

    safe_name = re.sub(r'[\[\]]', '', display_name).strip()
    safe_account_id = re.sub(r'[()]', '', account_id).strip()
    return f'@[{safe_name}]({safe_account_id})'


def render_mention_markup(display_name: str, account_id: str) -> str:
    """Builds the ``marklas`` mention span for a single user.

    Args:
        display_name: the display name of the mentioned user.
        account_id: the Jira ``accountId`` of the mentioned user.

    Returns:
        A ``marklas``-compatible ``<span adf="mention" ...>`` string that ``marklas.to_adf`` converts into an
        ADF ``mention`` node.
    """

    params = json.dumps({'id': account_id}, separators=(',', ':'), ensure_ascii=False)
    return f'<span adf="mention" params=\'{params}\'>@{display_name}</span>'


def expand_mention_tokens(markdown: str) -> str:
    """Replaces mention tokens in a Markdown string with ``marklas`` mention spans.

    Tokens that do not match :data:`MENTION_TOKEN_PATTERN` are left untouched and will be submitted as literal
    text.

    Args:
        markdown: the comment text in Markdown, possibly containing ``@[Name](accountId)`` tokens.

    Returns:
        The Markdown with every recognised mention token expanded to a ``marklas`` mention span. If the input
        contains no tokens it is returned unchanged.
    """

    if not markdown or '@[' not in markdown:
        return markdown
    return MENTION_TOKEN_PATTERN.sub(
        lambda match: render_mention_markup(match['name'], match['account_id']),
        markdown,
    )
