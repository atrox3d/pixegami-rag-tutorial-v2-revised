LOGGING_LEVEL = 15
LOGGING_LEVEL_NAME = 'TRACE'


import logging


class TraceLogger(logging.Logger):
    # 2. Add the custom level to the Logger class
    def trace(self, message, *args, **kws):
        """Logs a message with level 'TRACE' on this logger.

            The arguments are interpreted as for debug().
            :param message: The message format string
            :param args: Arguments which are merged into message.
            :param kws: Keyword arguments which are merged into message.
        """
        if self.isEnabledFor(LOGGING_LEVEL):
            self._log(LOGGING_LEVEL, message, args, **kws)


def setup_tracelogger():
    logging.addLevelName(
        LOGGING_LEVEL, 
        LOGGING_LEVEL_NAME
    )
    logging.setLoggerClass(TraceLogger)


def getLogger(name: str | None = None) -> TraceLogger:
    setup_tracelogger()
    return logging.getLogger(name)


setup_tracelogger()
