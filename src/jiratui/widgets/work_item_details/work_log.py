from typing import cast

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Collapsible, Footer, Link, Markdown

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraWorklog
from jiratui.utils.adf2md.adf2md import adf2md
from jiratui.utils.urls import build_external_url_for_work_log
from jiratui.widgets.base import CustomTitle


class WorkLogCollapsible(Collapsible):
    pass


class WorkItemWorkLogScreen(Screen):
    """A screen that displays the work log of a work item."""

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Close'),
    ]
    TITLE = 'Work Log'

    def __init__(self, work_item_key: str):
        super().__init__()
        self._work_item_key = work_item_key

    @property
    def work_log_items_container(self) -> VerticalScroll:
        return self.query_one(VerticalScroll)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield CustomTitle(f'{self.TITLE} for Item: {self._work_item_key}')
            yield VerticalScroll()
        yield Footer()

    async def on_mount(self) -> None:
        if self._work_item_key:
            self.run_worker(self.fetch_work_log())

    async def fetch_work_log(self) -> None:
        """Retrieves the work log data associated to a work item and updates the details ijn the screen.

        Returns:
            Nothing.
        """
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.get_work_item_worklog(
            self._work_item_key
        )
        if response.success:
            elements: list[WorkLogCollapsible] = []
            work_log: JiraWorklog
            for work_log in response.result.logs:
                comment_text = ''
                if work_log.comment:
                    try:
                        comment_text = adf2md(work_log.comment)
                    except Exception:
                        comment_text = 'Unable to display the comment associated to the log.'
                url = build_external_url_for_work_log(self._work_item_key, work_log.id)
                elements.append(
                    WorkLogCollapsible(
                        Link(
                            'Open link to the work log details',
                            url=url or '',
                            tooltip='view comment in the browser',
                        ),
                        Markdown(comment_text),
                        title=work_log.display(),
                    )
                )
            await self.work_log_items_container.mount_all(elements)
