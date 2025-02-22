import typer
import logging

import populate_database
import query_data

logger = logging.getLogger(__name__)
app = typer.Typer(no_args_is_help=True)


# use directly decorators instead of imported apps
# app.add_typer(populate_database.app, name='db')
app.command('db'  )(populate_database.main)
# app.add_typer(query_data.app, name='query')
app.command('query'  )(query_data.main)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()
