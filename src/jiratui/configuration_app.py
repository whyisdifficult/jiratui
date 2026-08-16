from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalGroup, ItemGrid, Vertical, VerticalScroll
from textual.screen import Screen
from textual.theme import BUILTIN_THEMES
from textual.widgets import Button, Checkbox, Input, Label, Select, Static
import yaml

from jiratui.api_controller.controller import APIController
from jiratui.config import ApplicationConfiguration, SSLConfiguration
from jiratui.constants import DEFAULT_JIRA_API_VERSION
from jiratui.files import get_config_file

BANNER = """
     ,--.,--.               ,--------.,--. ,--.,--.
     |  |`--',--.--. ,--,--.'--.  .--'|  | |  ||  |
,--. |  |,--.|  .--'' ,-.  |   |  |   |  | |  ||  |
|  '-'  /|  ||  |   \\ '-'  |   |  |   '  '-'  '|  |
 `-----' `--'`--'    `--`--'   `--'    `-----' `--'
v1.13.0
"""


class ConfigAppConfiguration(ApplicationConfiguration):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings,)


class ConfigurationInputWidget(Input):
    def __init__(self, *args, **kwargs):
        title = kwargs.pop('title', '')
        super().__init__(*args, compact=True, **kwargs)
        self.border_title = title


class ConfigurationScreen(Screen):
    def __init__(self, target_config_file: Path | None = None):
        super().__init__()
        self.__controller: APIController | None = None
        self.__using_default_config_file_location = False
        self.__default_config_location = get_config_file()
        if target_config_file:
            self.__configuration_file: Path = target_config_file
        else:
            self.__using_default_config_file_location = True
            self.__configuration_file = self.__default_config_location

    @property
    def button_save_widget(self) -> Button:
        return self.query_one('#button_save', expect_type=Button)

    @property
    def button_test_widget(self) -> Button:
        return self.query_one('#button_test', expect_type=Button)

    @property
    def jira_api_username_widget(self) -> ConfigurationInputWidget:
        return self.query_one('#jira_api_username', expect_type=ConfigurationInputWidget)

    @property
    def jira_api_token_widget(self) -> ConfigurationInputWidget:
        return self.query_one('#jira_api_token', expect_type=ConfigurationInputWidget)

    @property
    def jira_api_base_url_widget(self) -> ConfigurationInputWidget:
        return self.query_one('#jira_api_base_url', expect_type=ConfigurationInputWidget)

    @property
    def configuration_file_path_widget(self) -> ConfigurationInputWidget:
        return self.query_one('#configuration_file_path', expect_type=ConfigurationInputWidget)

    @property
    def use_bearer_authentication_widget(self) -> Checkbox:
        return self.query_one('#use_bearer_authentication', expect_type=Checkbox)

    @property
    def use_cert_authentication_widget(self) -> Checkbox:
        return self.query_one('#use_cert_authentication', expect_type=Checkbox)

    @property
    def configuration_file_path_message_widget(self) -> Label:
        return self.query_one('#configuration-file-path-message', expect_type=Label)

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes='configuration-vertical-scroll'):
            yield Static(BANNER).add_class('heading').add_class('banner')
            yield (
                Static(
                    'https://jiratui.sh | https://jiratui.readthedocs.io | https://github.com/whyisdifficult/jiratui',
                )
                .add_class('heading')
                .add_class('margin-bottom')
            )
            yield (
                Static(
                    'This application will help you generate a configuration for JiraTUI with the minimal required settings.',
                )
                .add_class('heading')
                .add_class('margin-bottom')
            )
            with HorizontalGroup(classes='configuration-container-jira-settings') as jira_settings:
                jira_settings.border_title = 'Minimal Settings'
                with Vertical(classes='configuration-container-api-settings') as api_settings:
                    api_settings.border_title = 'API'
                    api_base_url_widget = ConfigurationInputWidget(
                        id='jira_api_base_url',
                        placeholder='https://...',
                        classes='configuration-input required',
                        title='Jira Instance Base URL',
                    )
                    api_base_url_widget.border_subtitle = '(*)'
                    yield api_base_url_widget
                    api_username_widget = ConfigurationInputWidget(
                        id='jira_api_username',
                        placeholder='Enter your Jira username',
                        title='Jira API Username',
                        classes='configuration-input required',
                    )
                    api_username_widget.border_subtitle = '(*)'
                    yield api_username_widget
                    api_token_widget = ConfigurationInputWidget(
                        id='jira_api_token',
                        password=True,
                        placeholder='Enter your API token',
                        title='Jira API Token',
                        classes='configuration-input required',
                    )
                    api_token_widget.border_subtitle = '(*)'
                    yield api_token_widget
                    yield Checkbox(
                        id='cloud',
                        label='Use Jira Cloud',
                        compact=True,
                        classes='configuration-checkbox',
                        value=True,
                    )
                    yield Static(
                        'Check this if your Jira instance runs on the Cloud',
                        classes='configuration-tip',
                        shrink=True,
                    )
                    api_version_selection = Select(
                        id='jira_api_version',
                        options=[('Version 2', '2'), ('Version 3', '3')],
                        compact=True,
                        classes='configuration-selector',
                        value=str(DEFAULT_JIRA_API_VERSION),
                    )
                    api_version_selection.border_title = 'Jira API Version'
                    yield api_version_selection
                    yield Static(
                        'For Jira Cloud use 2 or 3. For Jira DC instances the version is always 2. Default is 3',
                        classes='configuration-tip',
                        shrink=True,
                    )
                    yield Checkbox(
                        id='use_bearer_authentication',
                        label='Use Bearer Authentication',
                        compact=True,
                        classes='configuration-checkbox',
                        value=False,
                    )
                    yield Static(
                        'Check if your Jira instance uses Bearer authentication instead of Basic authentication',
                        classes='configuration-tip',
                        shrink=True,
                    )
                    yield Checkbox(
                        id='use_cert_authentication',
                        label='Use Cert Authentication',
                        compact=True,
                        classes='configuration-checkbox',
                        value=False,
                    )
                    yield Static(
                        'Check this if your Jira instance uses certificate-based authentication instead of Bearer authentication or Basic authentication',
                        classes='configuration-tip',
                        shrink=True,
                    )
                with Vertical(classes='configuration-container-ssl-settings') as ssl_settings:
                    ssl_settings.border_title = 'SSL'
                    # SSL configuration
                    yield Checkbox(
                        id='verify_ssl',
                        label='Verify SSL',
                        classes='configuration-checkbox',
                        value=True,
                    )
                    yield ConfigurationInputWidget(
                        id='ca_bundle',
                        placeholder='Path to the CA bundle file',
                        classes='configuration-input',
                        title='CA Bundle File',
                    )
                    yield ConfigurationInputWidget(
                        id='certificate_file',
                        placeholder='Path to the a client-side certificate file, e.g. cert.pem',
                        classes='configuration-input',
                        title='Client-side Certificate File',
                    )
                    yield ConfigurationInputWidget(
                        id='key_file',
                        placeholder='Path to the key file',
                        classes='configuration-input',
                        title='Key File',
                    )
                    yield ConfigurationInputWidget(
                        id='password',
                        password=True,
                        placeholder='The password for the key file',
                        classes='configuration-input',
                        title='Key File Password',
                    )
                    with ItemGrid(classes='configuration-container-grid-test'):
                        yield Button(
                            'Test',
                            id='button_test',
                            variant='success',
                            classes='configuration-button',
                            disabled=True,
                        )
                        yield Static('', id='buton_test_message', classes='error')
            with ItemGrid(classes='configuration-container-grid-optional-settings'):
                yield ConfigurationInputWidget(
                    id='jira_account_id',
                    placeholder='E.g. 123456-4ca2-8885-343dff03be',
                    classes='configuration-input',
                    title='Your Jira User Account Id',
                )
                theme_selection = Select(
                    id='theme',
                    options=[(t, t) for t in BUILTIN_THEMES.keys()],
                    compact=True,
                    classes='configuration-selector',
                )
                theme_selection.border_title = 'Theme'
                yield theme_selection
                yield Static(
                    'The ID of the Jira user using the application. This is useful if you want the user selection dropdown widgets to automatically select your user from the options. It is also used as the default reporter of any new work item that is created in the application',
                    classes='configuration-tip',
                    shrink=True,
                )
                yield Static(
                    'If you don not choose a theme the default theme "textual-dark" will be used.',
                    classes='configuration-tip',
                    shrink=True,
                )
            with ItemGrid(classes='configuration-container-grid-file-save'):
                with Vertical():
                    yield ConfigurationInputWidget(
                        id='configuration_file_path',
                        placeholder='Enter the path to your configuration YAML file...',
                        classes='configuration-input',
                        title='Configuration File',
                    )
                    yield Label(
                        id='configuration-file-path-message',
                        content='Warning: Storing the config file in this location will require setting the env variable JIRA_TUI_CONFIG_FILE to start the app.',
                        classes='configuration-warning',
                        shrink=True,
                    ).add_class('invisible')
                with Vertical():
                    yield Button(
                        'Save',
                        id='button_save',
                        classes='configuration-button',
                        variant='success',
                        disabled=True,
                    )
            yield Static()

    def on_mount(self):
        self.configuration_file_path_widget.value = str(self.__configuration_file)
        username = self.jira_api_username_widget.value
        token = self.jira_api_token_widget.value
        url = self.jira_api_base_url_widget.value
        if username and username.strip() and token and token.strip() and url and url.strip():
            self.button_save_widget.disabled = False
        else:
            self.button_save_widget.disabled = True
        if self.__using_default_config_file_location:
            self.configuration_file_path_message_widget.add_class('invisible')
        else:
            self.configuration_file_path_message_widget.remove_class('invisible')

    @on(Select.Changed, '#theme')
    def toggle_theme(self, event: Select.Changed) -> None:
        if event.value and event.value != Select.NULL:
            self.app.theme = event.value
        else:
            self.app.theme = self.app.DEFAULT_THEME

    @on(Checkbox.Changed, '#use_cert_authentication')
    def toggle_use_bearer_authentication(self, event: Checkbox.Changed) -> None:
        if event.value:
            self.use_bearer_authentication_widget.value = False

    @on(Checkbox.Changed, '#use_bearer_authentication')
    def toggle_use_cert_authentication(self, event: Checkbox.Changed) -> None:
        if event.value:
            self.use_cert_authentication_widget.value = False

    @on(Input.Blurred, '#configuration_file_path')
    def validate_configuration_file_path(self, event: Input.Blurred):
        if event.value and (cleaned_value := event.value.strip()):
            self.button_save_widget.disabled = False
            if cleaned_value == str(self.__default_config_location):
                self.configuration_file_path_message_widget.add_class('invisible')
            else:
                self.configuration_file_path_message_widget.remove_class('invisible')
        else:
            self.button_save_widget.disabled = True
            self.configuration_file_path_message_widget.add_class('invisible')

    @on(Input.Blurred, '#jira_api_base_url')
    def validate_jira_api_base_url(self, event: Input.Blurred):
        username = self.jira_api_username_widget.value
        token = self.jira_api_token_widget.value
        if (
            username
            and username.strip()
            and token
            and token.strip()
            and event.value
            and event.value.strip()
        ):
            self.button_test_widget.disabled = False
            if self.configuration_file_path_widget.value:
                self.button_save_widget.disabled = False
            else:
                self.button_save_widget.disabled = True
        else:
            self.button_test_widget.disabled = True
            self.button_save_widget.disabled = True

    @on(Input.Blurred, '#jira_api_username')
    def validate_jira_api_username(self, event: Input.Blurred):
        token = self.jira_api_token_widget.value
        url = self.jira_api_base_url_widget.value
        if url and url.strip() and token and token.strip() and event.value and event.value.strip():
            self.button_test_widget.disabled = False
            if self.configuration_file_path_widget.value:
                self.button_save_widget.disabled = False
            else:
                self.button_save_widget.disabled = True
        else:
            self.button_test_widget.disabled = True
            self.button_save_widget.disabled = True

    @on(Input.Blurred, '#jira_api_token')
    def validate_jira_api_token(self, event: Input.Blurred):
        username = self.jira_api_username_widget.value
        url = self.jira_api_base_url_widget.value
        if (
            url
            and url.strip()
            and username
            and username.strip()
            and event.value
            and event.value.strip()
        ):
            self.button_test_widget.disabled = False
            if self.configuration_file_path_widget.value:
                self.button_save_widget.disabled = False
            else:
                self.button_save_widget.disabled = True
        else:
            self.button_test_widget.disabled = True
            self.button_save_widget.disabled = True

    @on(Button.Pressed, '#button_test')
    async def _button_test_connectivity(self) -> None:
        jira_api_username = self.jira_api_username_widget.value
        jira_api_token = self.jira_api_token_widget.value
        jira_api_base_url = self.jira_api_base_url_widget.value
        if jira_api_base_url and jira_api_token and jira_api_username:
            self.__controller = APIController(
                ConfigAppConfiguration(
                    jira_api_username=jira_api_username,
                    jira_api_token=jira_api_token,
                    jira_api_base_url=jira_api_base_url,
                )
            )
            response = await self.__controller.myself()  # type:ignore[attr-defined]
            buton_test_message_widget = self.query_one('#buton_test_message', expect_type=Static)
            if response.success:
                buton_test_message_widget.remove_class('error-message')
                buton_test_message_widget.add_class('success-message')
                buton_test_message_widget.content = 'Connection successful!'
            else:
                buton_test_message_widget.remove_class('success-message')
                buton_test_message_widget.add_class('error-message')
                buton_test_message_widget.content = f'Connection failed: {response.error}'
            await self.__controller.api.client.close_async_client()
            await self.__controller.api.async_http_client.close_async_client()
        else:
            self.notify(
                message='Missing required API URL and/or Username and/or Token',
                severity='error',
                title='Validation Error',
            )

    @on(Input.Blurred, '#ca_bundle')
    def validate_ca_bundle_path(self, event: Input.Blurred):
        if event.value:
            file_path = Path(event.value)
            if not file_path.exists():
                self.query_one('#ca_bundle', expect_type=ConfigurationInputWidget).add_class(
                    '-invalid'
                )
                self.notify(
                    severity='error', message='File does not exist', title='Validation Error'
                )
            else:
                self.query_one('#ca_bundle', expect_type=ConfigurationInputWidget).remove_class(
                    '-invalid'
                )

    @on(Input.Blurred, '#certificate_file')
    def validate_certificate_file_path(self, event: Input.Blurred):
        if event.value:
            file_path = Path(event.value)
            if not file_path.exists():
                self.query_one('#certificate_file', expect_type=ConfigurationInputWidget).add_class(
                    '-invalid'
                )
                self.notify(
                    severity='error', message='File does not exist', title='Validation Error'
                )
            else:
                self.query_one(
                    '#certificate_file', expect_type=ConfigurationInputWidget
                ).remove_class('-invalid')

    @on(Input.Blurred, '#key_file')
    def validate_key_file_path(self, event: Input.Blurred):
        if event.value:
            file_path = Path(event.value)
            if not file_path.exists():
                self.query_one('#key_file', expect_type=ConfigurationInputWidget).add_class(
                    '-invalid'
                )
                self.notify(
                    severity='error', message='File does not exist', title='Validation Error'
                )
            else:
                self.query_one('#key_file', expect_type=ConfigurationInputWidget).remove_class(
                    '-invalid'
                )

    def _check_for_non_default_ssl_configuration(self) -> dict[str, Any] | None:
        fields: dict[str, Any] = {
            'verify_ssl': self.query_one('#verify_ssl', expect_type=Checkbox).value
        }
        if ca_bundle := self.query_one('#ca_bundle', expect_type=ConfigurationInputWidget).value:
            fields['ca_bundle'] = ca_bundle
        if certificate_file := self.query_one(
            '#certificate_file', expect_type=ConfigurationInputWidget
        ).value:
            fields['certificate_file'] = certificate_file
        if key_file := self.query_one('#key_file', expect_type=ConfigurationInputWidget).value:
            fields['key_file'] = key_file
        if password := self.query_one('#password', expect_type=ConfigurationInputWidget).value:
            fields['password'] = password

        if not fields:
            return None
        return fields

    @on(Button.Pressed, '#button_save')
    async def _button_save(self) -> None:
        # keep track of the fields with non-default values to only dump these
        model_dump_include: set[str] = {
            'jira_api_username',
            'jira_api_token',
            'jira_api_base_url',
            'cloud',
            'use_bearer_authentication',
            'use_cert_authentication',
            'jira_api_version',
            'theme',
        }

        # build the config
        config = ConfigAppConfiguration(
            jira_api_username=self.jira_api_username_widget.value,
            jira_api_token=self.jira_api_token_widget.value,
            jira_api_base_url=self.jira_api_base_url_widget.value,
            cloud=self.query_one('#cloud', expect_type=Checkbox).value,
            use_bearer_authentication=self.query_one(
                '#use_bearer_authentication', expect_type=Checkbox
            ).value,
            use_cert_authentication=self.query_one(
                '#use_cert_authentication', expect_type=Checkbox
            ).value,
            theme=self.query_one('#theme', expect_type=Select).selection,
        )

        if (
            jira_api_version := self.query_one('#jira_api_version', expect_type=Select).selection
        ) is not None:
            config.jira_api_version = int(jira_api_version)

        # SSL configuration fields
        ssl_configuration: dict[str, Any] | None = self._check_for_non_default_ssl_configuration()
        if ssl_configuration:
            config.ssl = SSLConfiguration(
                verify_ssl=ssl_configuration.get('verify_ssl', True),
                ca_bundle=ssl_configuration.get('ca_bundle'),
                certificate_file=ssl_configuration.get('certificate_file'),
                key_file=ssl_configuration.get('key_file'),
                password=ssl_configuration.get('password'),
            )
            model_dump_include.update(set(ssl_configuration.keys()))
            model_dump_include.add('ssl')

        config_as_dict: dict = config.model_dump(include=model_dump_include)
        config_as_dict['jira_api_token'] = self.jira_api_token_widget.value
        yaml_data = yaml.dump(config_as_dict, default_flow_style=False, sort_keys=False)

        try:
            with open(self.configuration_file_path_widget.value, 'w') as file:
                file.write(yaml_data)
            self.notify(f'File saved successfully: {self.configuration_file_path_widget.value}')
        except Exception as e:
            self.notify(severity='error', message=str(e))


class JiraTUIConfigurationApp(App):
    CSS_PATH = 'css/config.tcss'
    """The path to the file with the TCSS (Textual CSS) definitions."""
    TITLE = 'JiraTUI Configuration Manager'
    DEFAULT_THEME = 'textual-dark'

    BINDINGS = [
        Binding(
            key='ctrl+q,q',
            action='quit',
            description='\U000023fb',
            key_display='^q',
            tooltip='Quit',
            show=True,
        )
    ]

    def __init__(self, output_file: str | None = None):
        super().__init__()
        self.__target_config_file = None
        if output_file:
            self.__target_config_file = Path(output_file)

    async def on_mount(self) -> None:
        await self.push_screen(ConfigurationScreen(target_config_file=self.__target_config_file))
