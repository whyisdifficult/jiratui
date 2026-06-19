from contextvars import ContextVar
from typing import Any


class ApplicationSession:
    """Session storage using Python's contextvars for async-safe isolation.

    Example:
    # create the session object
    session = ContextualSession()
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

    _session_var: ContextVar[dict[str, Any]] = ContextVar('application_session', default=None)

    @classmethod
    def _get_session(cls) -> dict[str, Any]:
        session = cls._session_var.get()
        if session is None:
            session = {}
            cls._session_var.set(session)
        return session

    def __setattr__(self, name: str, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._get_session()[name] = value

    def __getattr__(self, name: str):
        if name.startswith('_'):
            return super().__getattribute__(name)
        try:
            return self._get_session()[name]
        except KeyError as e:
            raise AttributeError(f"ApplicationSession has no attribute '{name}'") from e

    def get(self, name: str, default=None):
        return self._get_session().get(name, default)

    def clear(self):
        self._get_session().clear()
