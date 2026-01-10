from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.widgets.create_work_item.screen import AddWorkItemScreen


@pytest.fixture
def mock_api_controller():
    """Create a mock API controller for testing."""
    controller = Mock(spec=APIController)
    controller.search_projects = AsyncMock(
        return_value=APIControllerResponse(success=True, result=[])
    )
    controller.get_issue_types_for_project = AsyncMock(
        return_value=APIControllerResponse(success=True, result=[])
    )
    controller.search_users_assignable_to_projects = AsyncMock(
        return_value=APIControllerResponse(success=True, result=[])
    )
    return controller


@pytest.fixture
def create_metadata_with_editable_reporter():
    """Create metadata response where reporter field is editable."""
    return {
        'fields': [
            {
                'fieldId': 'reporter',
                'name': 'Reporter',
                'required': False,
                'operations': ['set'],  # 'set' operation means field is editable
                'schema': {
                    'type': 'user',
                    'system': 'reporter',
                },
            },
            {
                'fieldId': 'description',
                'name': 'Description',
                'required': False,
                'operations': ['set'],
            },
        ]
    }


@pytest.fixture
def create_metadata_without_editable_reporter():
    """Create metadata response where reporter field is NOT editable."""
    return {
        'fields': [
            {
                'fieldId': 'reporter',
                'name': 'Reporter',
                'required': False,
                'operations': [],  # No 'set' operation means field is NOT editable
                'schema': {
                    'type': 'user',
                    'system': 'reporter',
                },
            },
            {
                'fieldId': 'description',
                'name': 'Description',
                'required': False,
                'operations': ['set'],
            },
        ]
    }


@pytest.mark.asyncio
async def test_reporter_field_hidden_when_not_editable(
    app, mock_api_controller, create_metadata_without_editable_reporter
):
    """Test that reporter field is hidden when API metadata indicates it's not editable."""
    # Mock the API controller
    app.api = mock_api_controller
    mock_api_controller.get_issue_create_metadata = AsyncMock(
        return_value=APIControllerResponse(
            success=True, result=create_metadata_without_editable_reporter
        )
    )

    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST', reporter_account_id='user123')
        app.push_screen(screen)
        await pilot.pause()

        # Trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Assertions
        assert screen._reporter_is_editable is False, 'Reporter should not be editable'
        assert screen.reporter_selector.display is False, 'Reporter field should be hidden'


@pytest.mark.asyncio
async def test_reporter_field_shown_when_editable(
    app, mock_api_controller, create_metadata_with_editable_reporter
):
    """Test that reporter field is shown when API metadata indicates it's editable."""
    # Mock the API controller
    app.api = mock_api_controller
    mock_api_controller.get_issue_create_metadata = AsyncMock(
        return_value=APIControllerResponse(
            success=True, result=create_metadata_with_editable_reporter
        )
    )

    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST', reporter_account_id='user123')
        app.push_screen(screen)
        await pilot.pause()

        # Trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Assertions
        assert screen._reporter_is_editable is True, 'Reporter should be editable'
        assert screen.reporter_selector.display is True, 'Reporter field should be shown'


@pytest.mark.asyncio
async def test_validation_skips_reporter_when_not_editable(
    app, mock_api_controller, create_metadata_without_editable_reporter
):
    """Test that validation does not require reporter field when it's not editable."""
    # Mock the API controller
    app.api = mock_api_controller
    mock_api_controller.get_issue_create_metadata = AsyncMock(
        return_value=APIControllerResponse(
            success=True, result=create_metadata_without_editable_reporter
        )
    )

    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST')
        app.push_screen(screen)
        await pilot.pause()

        # Trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Mock the selection properties to return valid values
        with (
            patch.object(
                type(screen.project_selector), 'selection', new_callable=PropertyMock
            ) as mock_project,
            patch.object(
                type(screen.issue_type_selector), 'selection', new_callable=PropertyMock
            ) as mock_issue_type,
            patch.object(
                type(screen.reporter_selector), 'selection', new_callable=PropertyMock
            ) as mock_reporter,
            patch.object(
                type(screen.summary_field), 'value', new_callable=PropertyMock
            ) as mock_summary,
        ):
            mock_project.return_value = 'TEST'
            mock_issue_type.return_value = 'task-123'
            mock_reporter.return_value = None  # No reporter selected
            mock_summary.return_value = 'Test Summary'

            # Validation should pass even without reporter
            assert screen._validate_required_fields() is True, (
                "Validation should pass without reporter when it's not editable"
            )


@pytest.mark.asyncio
async def test_save_excludes_reporter_when_not_editable(
    app, mock_api_controller, create_metadata_without_editable_reporter
):
    """Test that save handler does not include reporter field when it's not editable."""
    # Mock the API controller
    app.api = mock_api_controller
    mock_api_controller.get_issue_create_metadata = AsyncMock(
        return_value=APIControllerResponse(
            success=True, result=create_metadata_without_editable_reporter
        )
    )

    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST')
        app.push_screen(screen)
        await pilot.pause()

        # Trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Mock dismiss
        screen.dismiss = Mock()

        # Mock the selection and value properties
        with (
            patch.object(
                type(screen.project_selector), 'selection', new_callable=PropertyMock
            ) as mock_project,
            patch.object(
                type(screen.issue_type_selector), 'selection', new_callable=PropertyMock
            ) as mock_issue_type,
            patch.object(
                type(screen.assignee_selector), 'selection', new_callable=PropertyMock
            ) as mock_assignee,
            patch.object(
                type(screen.reporter_selector), 'selection', new_callable=PropertyMock
            ) as mock_reporter,
            patch.object(
                type(screen.parent_key_field), 'value', new_callable=PropertyMock
            ) as mock_parent,
            patch.object(
                type(screen.summary_field), 'value', new_callable=PropertyMock
            ) as mock_summary,
            patch.object(
                type(screen.description_field), 'text', new_callable=PropertyMock
            ) as mock_description,
        ):
            mock_project.return_value = 'TEST'
            mock_issue_type.return_value = 'task-123'
            mock_assignee.return_value = 'assignee123'
            mock_reporter.return_value = 'reporter123'  # Set but should be ignored
            mock_parent.return_value = None
            mock_summary.return_value = 'Test Summary'
            mock_description.return_value = 'Test Description'

            # Trigger save
            screen.handle_save()

        # Get the data passed to dismiss
        dismiss_args = screen.dismiss.call_args[0][0]

        # Assertions
        assert 'reporter_account_id' not in dismiss_args, (
            'Reporter should not be included in save data when not editable'
        )
        assert dismiss_args['project_key'] == 'TEST'
        assert dismiss_args['summary'] == 'Test Summary'


@pytest.mark.asyncio
async def test_save_includes_reporter_when_editable(
    app, mock_api_controller, create_metadata_with_editable_reporter
):
    """Test that save handler includes reporter field when it's editable."""
    # Mock the API controller
    app.api = mock_api_controller
    mock_api_controller.get_issue_create_metadata = AsyncMock(
        return_value=APIControllerResponse(
            success=True, result=create_metadata_with_editable_reporter
        )
    )

    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST', reporter_account_id='reporter123')
        app.push_screen(screen)
        await pilot.pause()

        # Trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Mock dismiss
        screen.dismiss = Mock()

        # Mock the selection and value properties
        with (
            patch.object(
                type(screen.project_selector), 'selection', new_callable=PropertyMock
            ) as mock_project,
            patch.object(
                type(screen.issue_type_selector), 'selection', new_callable=PropertyMock
            ) as mock_issue_type,
            patch.object(
                type(screen.assignee_selector), 'selection', new_callable=PropertyMock
            ) as mock_assignee,
            patch.object(
                type(screen.reporter_selector), 'selection', new_callable=PropertyMock
            ) as mock_reporter,
            patch.object(
                type(screen.parent_key_field), 'value', new_callable=PropertyMock
            ) as mock_parent,
            patch.object(
                type(screen.summary_field), 'value', new_callable=PropertyMock
            ) as mock_summary,
            patch.object(
                type(screen.description_field), 'text', new_callable=PropertyMock
            ) as mock_description,
        ):
            mock_project.return_value = 'TEST'
            mock_issue_type.return_value = 'task-123'
            mock_assignee.return_value = 'assignee123'
            mock_reporter.return_value = 'reporter123'
            mock_parent.return_value = None
            mock_summary.return_value = 'Test Summary'
            mock_description.return_value = 'Test Description'

            # Trigger save
            screen.handle_save()

        # Get the data passed to dismiss
        dismiss_args = screen.dismiss.call_args[0][0]

        # Assertions
        assert 'reporter_account_id' in dismiss_args, (
            'Reporter should be included in save data when editable'
        )
        assert dismiss_args['reporter_account_id'] == 'reporter123'
        assert dismiss_args['project_key'] == 'TEST'
        assert dismiss_args['summary'] == 'Test Summary'
