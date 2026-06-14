from textual.message import Message


class SearchWorkItem(Message):
    """A message posted by a widget when the user wants to search and fetch the details of a work item base don its
    key."""

    def __init__(self, work_item_key: str):
        self.work_item_key = work_item_key
        super().__init__()
