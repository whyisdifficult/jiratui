import dataclasses
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class HistoryEntry:
    key: str
    item_type: str
    status: str
    summary: str
    added: float = dataclasses.field(
        default_factory=lambda: int(datetime.now(tz=timezone.utc).timestamp())
    )


class HistoryManager:
    """Implements logic to manage the recent history of work items created, updated and viewed."""

    LIMIT = 20
    """Maximum number of items in the history. Items are evicted based on the time they were added."""

    def __init__(self):
        self.__history: dict[str, HistoryEntry] = {}

    def add_work_item(self, entry: HistoryEntry) -> None:
        """Adds or updates a work item in the history, maintaining the LIMIT size limit.

        If the item is already in the history it gets updated. If the item is not in the history it gets added. If
        the number of items in the history reaches the LIMIT then the oldest item is removed before adding the new one.

        Args:
            entry: the entry to be added to the history.

        Returns:
            None
        """

        # update timestamp for new or existing entries
        entry.added = int(datetime.now(tz=timezone.utc).timestamp())

        # if entry exists, just update it
        if entry.key in self.__history:
            self.__history[entry.key] = entry
            return

        # if at capacity, remove the oldest entry
        if len(self.__history) >= self.LIMIT:
            oldest_key = min(self.__history, key=lambda k: self.__history[k].added)
            del self.__history[oldest_key]

        # add the new entry
        self.__history[entry.key] = entry

    def delete_work_item(self, key: str) -> None:
        """Deletes a work item from the history.

        Args:
            key: the key of the work item to remove.

        Returns:
            None
        """

        if key in self.__history:
            del self.__history[key]

    def get_history(self) -> list[HistoryEntry]:
        """Retrieves the items in the history.

        Returns: a list of `HistoryEntry`.
        """

        if self.__history:
            return list(self.__history.values())
        return []

    def empty(self) -> None:
        """Empties the history."""
        self.__history = {}
