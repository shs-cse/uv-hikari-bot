import pygsheets
from pygsheets.exceptions import * # noqa:F403
from bot_environment.config import FilePath


# authorization
def get_google_client() -> pygsheets.client.Client:
    return pygsheets.authorize(client_secret=FilePath.GOOGLE_CREDENTIALS)