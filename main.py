import typer
import logging
from dotenv import load_dotenv

import tracelogger
import populate_database
import query_data


load_dotenv()
app = typer.Typer(no_args_is_help=True)


# use directly decorators instead of imported apps
# app.add_typer(populate_database.app, name='db')
app.command('db'  )(populate_database.main)
# app.add_typer(query_data.app, name='query')
app.command('query'  )(query_data.main)


if __name__ == "__main__":
    logger = tracelogger.getLogger(__name__)
    logging.basicConfig(
        level=tracelogger.LOGGING_LEVEL,
        # format='%(levelname)s:%(name)s:%(message)s'
        format='%(levelname)-10s | %(name)20s | %(funcName)20s | %(message)s'
    )
    logger.debug('test debug')
    logger.trace('test trace')
    
    app()

