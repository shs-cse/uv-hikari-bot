from pathlib import Path
from bot_environment.config import FileName
from wrappers.utils import FormatText
from wrappers.pygs import get_google_client
from wrappers.pygs import AuthenticationError

def check_google_credentials() -> None:
    print(FormatText.wait("Checking google credentials..."))
    if not Path(FileName.SHEETS_CREDENTIALS).exists():
        log = f'Sheets credential file "{FileName.SHEETS_CREDENTIALS}" was not found.'
        log += " You will need to log on by clicking on this following link"
        log += " and pasting the code from browser."
        print(FormatText.warning(log))
    try:
        get_google_client()
        print(FormatText.success("Google authorization was successful."))
    except Exception as error:
        log = "Google authorization failed!"
        log += " Did you forget to provide the correct credentials.json file?"
        raise AuthenticationError(FormatText.error(log)) from error
    

