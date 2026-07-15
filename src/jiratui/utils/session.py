from typing import Any


class ApplicationSession:
    """Session storage using a simple class-level dict for persistent session across the lifetime of the app.

    Example:
    # create the session object
    session = ApplicationSession()
    # set a variable
    session.some_variable = 42
    # if you know the variable has been set you can retrieve its value using
    value = session.get('some_variable')
    # with explicit default value
    value = session.get('some_variable', default=1)
    # or, if you don't know whether the variable has been set or not
    try:
        value = session.some_variable
    except AttributeError:
        value = None
    # clear the session
    session.clear()
    """

    __session: dict[str, Any] = {}  # Class-level shared storage

    def __setattr__(self, name: str, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            ApplicationSession.__session[name] = value

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return super().__getattribute__(name)
        try:
            return ApplicationSession.__session[name]
        except KeyError as e:
            raise AttributeError(f"ApplicationSession has no attribute '{name}'") from e

    def get(self, name: str, default=None) -> Any:
        return ApplicationSession.__session.get(name, default)

    def clear(self) -> None:
        ApplicationSession.__session.clear()
