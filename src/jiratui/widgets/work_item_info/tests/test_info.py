from jiratui.widgets.work_item_info.info import WorkItemInfoContainer


class TestExtractAdf:
    """Test the _extract_adf helper function."""

    def test_extract_adf_with_dict(self):
        """Test that _extract_adf handles dict input correctly."""
        container = WorkItemInfoContainer()

        adf_doc = {
            'type': 'doc',
            'version': 1,
            'content': [
                {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello World'}]}
            ],
        }

        result = container._extract_adf(adf_doc)

        assert isinstance(result, str)
        assert len(result) > 0
        assert 'Hello World' in result or 'Hello' in result

    def test_extract_adf_with_invalid_data(self):
        """Test that _extract_adf handles errors gracefully."""
        container = WorkItemInfoContainer()

        result = container._extract_adf(None)
        assert result == ''

        result = container._extract_adf({})
        assert result == ''

    def test_extract_adf_with_complex_adf(self):
        """Test _extract_adf with more complex ADF structure."""
        container = WorkItemInfoContainer()

        adf_doc = {
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'heading',
                    'attrs': {'level': 1},
                    'content': [{'type': 'text', 'text': 'Test Heading'}],
                },
                {
                    'type': 'paragraph',
                    'content': [
                        {'type': 'text', 'text': 'Test paragraph with ', 'marks': []},
                        {'type': 'text', 'text': 'bold text', 'marks': [{'type': 'strong'}]},
                    ],
                },
            ],
        }

        result = container._extract_adf(adf_doc)

        assert isinstance(result, str)
        assert len(result) > 0
