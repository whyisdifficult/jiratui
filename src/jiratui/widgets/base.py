from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input, MaskedInput, Rule, Static


class DateInput(MaskedInput):
    """A `MaskedInput` widget to hold date values."""

    TEMPLATE = '9999-99-99'
    PLACEHOLDER = '2025-12-23'
    LABEL = 'Date'
    TOOLTIP = ''
    ID: str | None = None
    CLASSES = 'input-date'
    BORDER_SUBTITLE = ''

    def __init__(self, widget_id: str | None = None, valid_empty: bool = True):
        super().__init__(
            id=widget_id or self.ID,
            template=self.TEMPLATE,
            placeholder=self.PLACEHOLDER,
            classes=self.CLASSES,
            tooltip=self.TOOLTIP,
            valid_empty=valid_empty,
        )
        self.border_title = self.LABEL
        if self.BORDER_SUBTITLE:
            self.border_subtitle = self.BORDER_SUBTITLE
        if not self.valid_empty:
            self.add_class('required')
            self.border_subtitle = f'{self.border_subtitle} (*)'


class ReadOnlyField(Input):
    def __init__(self, **kwargs):
        classes = kwargs.pop('classes', '')
        super().__init__(**kwargs)
        self.disabled = True
        if classes:
            self.add_class(*classes.split(','))


class ReadOnlyTextField(ReadOnlyField):
    def __init__(self, **kwargs):
        extra_classes = kwargs.pop('extra_classes', '')
        label = kwargs.pop('label', '')
        super().__init__(**kwargs)
        self.classes = 'issue_details_input_field'
        self.border_title = label
        if extra_classes:
            self.add_class(*extra_classes.split(','))


class CustomTitle(Widget):
    DEFAULT_CSS = """
    CustomTitle {
        layout: vertical;
        height: auto;
        align: center middle;
    }
    CustomTitle > Rule {
        color: $primary;
    }
    Rule.-horizontal {
        height: 1;
        margin: 0 0;
        width: 1fr;
    }
    """

    def __init__(self, title: str) -> None:
        self.title = title
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Rule()
        yield Static(Text(self.title, justify='center'))
        yield Rule()
