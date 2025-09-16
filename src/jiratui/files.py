from pathlib import Path

from xdg_base_dirs import xdg_config_home, xdg_state_home

from jiratui.constants import LOG_FILE_FILE_NAME


def _jiratui_directory(root: Path) -> Path:
    """Returns the path to a `jiratui` directory associated with the application.

    Args:
        root: the root directory path where the jiratui directory exists or is created.

    Returns:
        A `Path` expression of a `jiratui` directory.
    """
    directory = root / 'jiratui'
    directory.mkdir(exist_ok=True, parents=True)
    return directory


def get_config_directory() -> Path:
    """Retrieves the (default) directory where the configuration file of the application will be stored.

    Returns:
        A `Path` of the config directory.
    """
    return _jiratui_directory(xdg_config_home())


def get_logs_directory() -> Path:
    """Retrieves the (default) directory where the logs of the application will be stored.

    Returns:
        A `Path` of the logs directory.
    """
    return _jiratui_directory(xdg_state_home())


def get_config_file() -> Path:
    """Retrieves the (default) path of the config file.

    Returns:
        A `Path` of the config file.
    """
    return get_config_directory() / 'config.yaml'


def get_log_file() -> Path:
    """Retrieves the (default) path of the logs file.

    Returns:
        A `Path` of the logs file.
    """
    return get_logs_directory() / LOG_FILE_FILE_NAME
