import os
from pathlib import Path

import yaml

from jiratui.actions.constants import KEY_BINDINGS_LEGACY, KEY_BINDINGS_STANDARD
from jiratui.files import get_config_file


# TODO move to separate module and reuse with the ine in Config.py
def _get_config_file() -> Path:
    if jira_tui_config_file := os.getenv('JIRA_TUI_CONFIG_FILE'):
        conf_file = Path(jira_tui_config_file).resolve()
    else:
        conf_file = get_config_file()
    if not conf_file.exists():
        raise FileNotFoundError(f'Unable to find the config file you provided: {conf_file}')
    return conf_file


def _load_keybindings_style_from_configuration_file() -> str:
    try:
        config_file = _get_config_file()
    except FileNotFoundError:
        return 'legacy'
    else:
        with open(config_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
            style = yaml_data.get('key_bindings_style')
    return style


def _get_keybindings_style() -> str:
    if jira_tui_keybind_style := os.environ.get('JIRA_TUI_KEYBIND_STYLE'):
        return jira_tui_keybind_style
    return load_keybinding_style_into_environment()


def load_keybinding_style_into_environment() -> str:
    """Loads from the configuration file the actions style selected by the user and stores it in the environment
    variable `JIRA_TUI_KEYBIND_STYLE`.

    Returns:
        The style chosen by the user.
    """

    style: str = _load_keybindings_style_from_configuration_file()
    os.environ['JIRA_TUI_KEYBIND_STYLE'] = style
    return style


def get_application_key_bindings() -> dict:
    """Retrieves the applicable actions configuration based on the style selected by the user in the configuration
    file.

    Returns:
        A dict with the actions.
    """

    style: str = _get_keybindings_style()
    style_cleaned = style.lower().strip() if style else ''
    return KEY_BINDINGS_STANDARD if style_cleaned == 'standard' else KEY_BINDINGS_LEGACY
