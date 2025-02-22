import typer
import logging
from dotenv import load_dotenv

import populate_database
import query_data


load_dotenv()
logger = logging.getLogger(__name__)
app = typer.Typer(no_args_is_help=True)


# use directly decorators instead of imported apps
# app.add_typer(populate_database.app, name='db')
app.command('db'  )(populate_database.main)
# app.add_typer(query_data.app, name='query')
app.command('query'  )(query_data.main)


MY_DEBUG_LEVEL = 15
logging.addLevelName(MY_DEBUG_LEVEL, "trace")


# 2. Add the custom level to the Logger class
def trace(self, message, *args, **kws):
    """Logs a message with level 'MYDEBUG' on this logger.

    The arguments are interpreted as for debug().
    """
    if self.isEnabledFor(MY_DEBUG_LEVEL):
        self._log(MY_DEBUG_LEVEL, message, args, **kws)

logging.Logger.trace = trace


if __name__ == "__main__":
    logging.basicConfig(level=MY_DEBUG_LEVEL)
    logger.debug('test debug')
    logger.trace('test trace')
    app()
