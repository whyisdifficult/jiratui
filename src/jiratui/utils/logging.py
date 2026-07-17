class JiraTUILogger:
    def __init__(self, logger, enable_logging: bool = False):
        self.logger = logger
        self.__logging_enabled = enable_logging

    @property
    def logging_enabled(self) -> bool:
        return self.__logging_enabled

    @staticmethod
    def _get_stack_level(self, **kwargs) -> int:
        return int(kwargs.pop('stacklevel', 2))

    def debug(self, message, *args, **kwargs) -> None:
        if self.logging_enabled:
            stack_level = self._get_stack_level(kwargs)
            return self.logger.debug(message, *args, **kwargs, stacklevel=stack_level)
        return None

    def info(self, message, *args, **kwargs) -> None:
        if self.logging_enabled:
            stack_level = self._get_stack_level(kwargs)
            return self.logger.info(message, *args, **kwargs, stacklevel=stack_level)
        return None

    def warning(self, message, *args, **kwargs) -> None:
        if self.logging_enabled:
            stack_level = self._get_stack_level(kwargs)
            return self.logger.warning(message, *args, **kwargs, stacklevel=stack_level)
        return None

    def error(self, message, *args, **kwargs) -> None:
        if self.logging_enabled:
            stack_level = self._get_stack_level(kwargs)
            return self.logger.error(message, *args, **kwargs, stacklevel=stack_level)
        return None

    def log(self, message, *args, **kwargs) -> None:
        if self.logging_enabled:
            stack_level = self._get_stack_level(kwargs)
            return self.logger.log(message, *args, **kwargs, stacklevel=stack_level)
        return None

    def exception(self, message, *args, **kwargs) -> None:
        if self.logging_enabled:
            stack_level = self._get_stack_level(kwargs)
            return self.logger.exception(message, *args, **kwargs, stacklevel=stack_level)
        return None
