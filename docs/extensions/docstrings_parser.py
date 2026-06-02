import re

from docutils import nodes  # type: ignore
from myst_parser.parsers.sphinx_ import MystParser


class GoogleStyleDocstringParser(MystParser):
    def parse(self, inputstring: str, document: nodes.document) -> None:
        parsed_content = self._parse_google_style_docstring(inputstring)
        return super().parse(parsed_content, document)

    def _parse_google_style_docstring(self, docstring: str) -> str:
        description, params, returns, raises, examples = self._extract_sections(docstring)
        myst_docstring = description + '\n\n'

        if params:
            myst_docstring += '```{eval-rst}\n'
            for param in params:
                myst_docstring += f':param {param[0]}: {param[1]}\n'
            myst_docstring += '```\n\n'

        if returns:
            myst_docstring += '```{eval-rst}\n'
            myst_docstring += f':returns: {returns[0]}\n'
            myst_docstring += '```\n\n'

        if raises:
            myst_docstring += '```{eval-rst}\n'
            for exc in raises:
                myst_docstring += f':raises {exc[0]}: {exc[1]}\n'
            myst_docstring += '```\n\n'

        if examples:
            myst_docstring += '**Examples**\n'
            myst_docstring += '```\n'
            myst_docstring += examples
            myst_docstring += '\n```\n\n'

        return myst_docstring.strip()

    def _extract_sections(self, docstring: str):
        description = self._extract_description(docstring)
        params = self._extract_params(docstring)
        returns = self._extract_returns(docstring)
        raises = self._extract_raises(docstring)
        examples = self._extract_examples(docstring)
        return description, params, returns, raises, examples

    @staticmethod
    def _extract_description(docstring: str) -> str:
        # This regex captures everything up to the first section heading (if any)
        match = re.search(r'(Args|Returns|Raises|Example|Examples):', docstring)
        if match:
            return docstring[: match.span()[0]]
        return docstring

    @staticmethod
    def _extract_params(docstring: str):
        params = []
        param_section = re.search(r'Args:\n(.*?)(?=\n[A-Z][a-z]+:|\n\n|$)', docstring, re.S)
        if param_section:
            param_matches = re.findall(
                r'\s*([\w_]+):\s*(.*?)\s*(?=\n\s*[\w_]+:|\n\n|$)', param_section.group(1), re.S
            )
            params.extend(param_matches)
        return params

    @staticmethod
    def _extract_returns(docstring: str):
        return_section = re.search(r'Returns:\n(.*?)(?=\n[A-Z][a-z]+:|\n\n|$)', docstring, re.S)
        if return_section:
            match = re.match(r'\s*(.*?)\s*(?=\n\n|$)', return_section.group(1), re.S)
            if match:
                return match.groups()
        return None

    @staticmethod
    def _extract_raises(docstring: str):
        raises = []
        raises_section = re.search(r'Raises:\n(.*?)(?=\n[A-Z][a-z]+:|\n\n|$)', docstring, re.S)
        if raises_section:
            raise_matches = re.findall(
                r'\s*([\w_]+):\s*(.*?)\s*(?=\n\s*[\w_]+:|\n\n|$)', raises_section.group(1), re.S
            )
            for match in raise_matches:
                raises.append(match)
        return raises

    @staticmethod
    def _extract_examples(docstring: str):
        examples_section = re.search(r'Examples?:\n(.*?)(?=\n[A-Z][a-z]+:|\n\n|$)', docstring, re.S)
        return examples_section.group(1).strip() if examples_section else ''


Parser = GoogleStyleDocstringParser
