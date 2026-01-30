def replace_media_with_text(adf: dict) -> dict:
    """Replace mediaSingle nodes with inline text nodes showing attachment reference.

    This ensures attachment references appear inline where the media is in the document,
    not appended at the end.

    Args:
        adf: ADF document structure

    Returns:
        Modified ADF with mediaSingle replaced by text nodes

    Example:
        >>> adf = {
        ...     'type': 'paragraph',
        ...     'content': [
        ...         {'type': 'text', 'text': 'See '},
        ...         {'type': 'mediaSingle', 'content': [{'type': 'media', 'attrs': {'alt': 'screenshot.png'}}]},
        ...         {'type': 'text', 'text': ' for details.'},
        ...     ],
        ... }
        >>> result = replace_media_with_text(adf)
        >>> # Result has mediaSingle replaced with text node containing "(See file...)"
    """
    if not isinstance(adf, dict):
        return adf

    # Process content array to replace mediaSingle nodes
    if 'content' in adf and isinstance(adf['content'], list):
        new_content = []

        for node in adf['content']:
            # If this is a mediaSingle node, replace with text
            if node.get('type') == 'mediaSingle':
                # Extract filename from media node
                media_content = node.get('content', [])
                for media in media_content:
                    if isinstance(media, dict) and media.get('type') == 'media':
                        attrs = media.get('attrs', {})
                        filename = attrs.get('alt', 'unknown')
                        # Create paragraph with inline text node (italic markdown)
                        para_node = {
                            'type': 'paragraph',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': f'(See file "{filename}" in attachments tab)',
                                    'marks': [{'type': 'em'}],
                                }
                            ],
                        }
                        new_content.append(para_node)
                        break
            else:
                # Recursively process this node
                new_content.append(replace_media_with_text(node))

        adf = adf.copy()
        adf['content'] = new_content

    return adf


def extract_media_references(adf_data: dict) -> list[str]:
    """Extract media file names from mediaSingle nodes in ADF content.

    DEPRECATED: Use replace_media_with_text() instead for inline attachment references.

    Args:
        adf_data: ADF document structure (dict with 'type' and 'content')

    Returns:
        List of media file names (from 'alt' attribute)

    Example:
        >>> adf = {
        ...     'type': 'doc',
        ...     'content': [
        ...         {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello'}]},
        ...         {'type': 'mediaSingle', 'content': [{'type': 'media', 'attrs': {'alt': 'screenshot.png'}}]},
        ...     ],
        ... }
        >>> extract_media_references(adf)
        ['screenshot.png']
    """
    media_files = []

    def walk_nodes(node):
        """Recursively walk ADF tree to find mediaSingle nodes."""
        if not isinstance(node, dict):
            return

        node_type = node.get('type')

        # Found a mediaSingle node - extract media info
        if node_type == 'mediaSingle':
            content = node.get('content', [])
            for child in content:
                if isinstance(child, dict) and child.get('type') == 'media':
                    attrs = child.get('attrs', {})
                    filename = attrs.get('alt', '')
                    if filename:
                        media_files.append(filename)

        # Recurse into nested content
        if 'content' in node:
            for child in node.get('content', []):
                walk_nodes(child)

    walk_nodes(adf_data)
    return media_files


def extract_mention_references(adf_data: dict) -> list[dict]:
    """Extract mention nodes from ADF content.

    Args:
        adf_data: ADF document structure (dict with 'type' and 'content')

    Returns:
        List of dictionaries containing account_id and text from mention nodes

    Example:
        >>> adf = {
        ...     'type': 'doc',
        ...     'content': [
        ...         {
        ...             'type': 'paragraph',
        ...             'content': [
        ...                 {
        ...                     'type': 'mention',
        ...                     'attrs': {
        ...                         'id': 'xxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
        ...                         'text': '@Placeholder User',
        ...                     },
        ...                 }
        ...             ],
        ...         }
        ...     ],
        ... }
        >>> extract_mention_references(adf)
        [{'account_id': 'xxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', 'text': '@Placeholder User'}]
    """
    mentions = []

    def walk_nodes(node):
        """Recursively walk ADF tree to find mention nodes."""
        if not isinstance(node, dict):
            return

        node_type = node.get('type')

        # Found a mention node - extract attrs
        if node_type == 'mention':
            attrs = node.get('attrs', {})
            account_id = attrs.get('id')
            text = attrs.get('text')

            # Only add if both required fields present
            if account_id and text:
                mentions.append(
                    {
                        'account_id': account_id,
                        'text': text,
                    }
                )

        # Recurse into content
        if 'content' in node:
            for child in node.get('content', []):
                walk_nodes(child)

    walk_nodes(adf_data)
    return mentions


def format_mention_as_link(mention: dict, base_url: str | None) -> str:
    """Format mention as markdown hyperlink to Jira user profile.

    Args:
        mention: Dictionary with 'account_id' and 'text' keys
        base_url: Base URL of Jira instance (e.g., 'https://example.atlassian.net')
                  If None or empty, returns plain mention text

    Returns:
        Markdown hyperlink or plain text fallback

    Example:
        >>> mention = {'account_id': '712020:abc', 'text': '@User'}
        >>> format_mention_as_link(mention, 'https://example.atlassian.net')
        '[@User](https://example.atlassian.net/jira/people/712020:abc)'

        >>> format_mention_as_link(mention, None)
        '@User'
    """
    text = mention.get('text', '')
    account_id = mention.get('account_id', '')

    # Fallback to plain text if no base_url
    if not base_url:
        return text

    # Remove trailing slash from base_url if present
    base_url = base_url.rstrip('/')

    # Format as markdown link to Jira user profile page
    user_url = f'{base_url}/jira/people/{account_id}'
    return f'[{text}]({user_url})'


def fix_adf_text_with_marks(adf: dict) -> dict:
    """Pre-process ADF to fix text nodes with strong/em marks.

    atlas_doc_parser outputs malformed markdown when text content has
    trailing spaces inside strong/em marks. This function strips those
    trailing spaces and ensures proper spacing between elements.

    Args:
        adf: ADF structure (dict or any type)

    Returns:
        Fixed ADF structure with trailing spaces removed from marked text
    """
    if not isinstance(adf, dict):
        return adf

    # Process paragraph/list content to fix spacing
    if 'content' in adf and isinstance(adf['content'], list):
        new_content = []

        for i, node in enumerate(adf['content']):
            # Recursively process this node first
            node = fix_adf_text_with_marks(node)

            # Check if this text node has strong/em marks and trailing/leading spaces
            if node.get('type') == 'text' and 'marks' in node and 'text' in node:
                marks = node.get('marks', [])
                has_strong_or_em = any(
                    m.get('type') in ('strong', 'em') for m in marks if isinstance(m, dict)
                )

                if has_strong_or_em:
                    original_text = node['text']
                    stripped_text = original_text.strip()
                    had_trailing_space = original_text.endswith(' ')
                    had_leading_space = original_text.startswith(' ')

                    if stripped_text != original_text:
                        # Update node with stripped text
                        node = node.copy()
                        node['text'] = stripped_text

                        # Add leading spacer if needed
                        if had_leading_space and i > 0:
                            new_content.append({'type': 'text', 'text': ' '})

                        new_content.append(node)

                        # Add trailing spacer if there's a next element
                        if had_trailing_space and i < len(adf['content']) - 1:
                            new_content.append({'type': 'text', 'text': ' '})
                        continue

            new_content.append(node)

        adf = adf.copy()
        adf['content'] = new_content

    return adf


def fix_codeblock_in_list(adf: dict) -> dict:
    """Fix codeBlock nodes nested inside listItem nodes.

    atlas_doc_parser doesn't handle codeBlock inside listItem correctly - it renders
    an empty code fence and the content appears as plain text. This function lifts
    codeBlocks out of listItems and places them as siblings after the list, removing
    the empty list item.

    Args:
        adf: ADF document structure

    Returns:
        Modified ADF with codeBlocks extracted from listItems and empty items removed

    Example:
        Before:
        bulletList -> listItem -> codeBlock -> text

        After:
        bulletList (without that item)
        codeBlock -> text
    """
    if not isinstance(adf, dict):
        return adf

    # Process content array
    if 'content' in adf and isinstance(adf['content'], list):
        new_content = []
        extracted_codeblocks = []

        for node in adf['content']:
            # Recursively process the node first
            node = fix_codeblock_in_list(node)

            # Check if this is a bulletList or orderedList
            if node.get('type') in ('bulletList', 'orderedList'):
                list_items = node.get('content', [])
                new_list_items = []

                for item in list_items:
                    if item.get('type') == 'listItem':
                        item_content = item.get('content', [])
                        new_item_content = []
                        has_codeblock = False

                        for child in item_content:
                            # If we find a codeBlock inside listItem, extract it
                            if child.get('type') == 'codeBlock':
                                has_codeblock = True
                                # Save codeBlock to insert after the list
                                extracted_codeblocks.append(child)
                            else:
                                new_item_content.append(child)

                        # Only keep the list item if it has non-codeBlock content
                        if not has_codeblock or new_item_content:
                            item = item.copy()
                            item['content'] = new_item_content
                            new_list_items.append(item)
                    else:
                        new_list_items.append(item)

                # Only include the list if it still has items
                if new_list_items:
                    node = node.copy()
                    node['content'] = new_list_items
                    new_content.append(node)
            else:
                new_content.append(node)

            # Add extracted codeBlocks after the current node
            new_content.extend(extracted_codeblocks)
            extracted_codeblocks = []

        adf = adf.copy()
        adf['content'] = new_content

    return adf

    # Process content array
    if 'content' in adf and isinstance(adf['content'], list):
        new_content = []
        extracted_codeblocks = []

        for node in adf['content']:
            # Recursively process the node first
            node = fix_codeblock_in_list(node)

            # Check if this is a bulletList or orderedList
            if node.get('type') in ('bulletList', 'orderedList'):
                list_items = node.get('content', [])
                new_list_items = []

                for item in list_items:
                    if item.get('type') == 'listItem':
                        item_content = item.get('content', [])
                        new_item_content = []

                        for child in item_content:
                            # If we find a codeBlock inside listItem, extract it
                            if child.get('type') == 'codeBlock':
                                # Replace with placeholder text in the list item
                                new_item_content.append(
                                    {
                                        'type': 'paragraph',
                                        'content': [
                                            {'type': 'text', 'text': '(see code block below)'}
                                        ],
                                    }
                                )
                                # Save codeBlock to insert after the list
                                extracted_codeblocks.append(child)
                            else:
                                new_item_content.append(child)

                        # Update list item with new content
                        item = item.copy()
                        item['content'] = new_item_content
                        new_list_items.append(item)
                    else:
                        new_list_items.append(item)

                # Update list node with new items
                node = node.copy()
                node['content'] = new_list_items

            new_content.append(node)

            # Add extracted codeBlocks after the current node
            new_content.extend(extracted_codeblocks)
            extracted_codeblocks = []

        adf = adf.copy()
        adf['content'] = new_content

    return adf
