from bot_environment import state
from bot_environment.config import FilePath, InfoField, EnrolmentSprdsht, TemplateLink
from wrappers import pygs
from wrappers.utils import FormatText, update_info_key
from wrappers.pygs import get_google_client, get_spreadsheet, copy_spreadsheet
from wrappers.pygs import update_cells_from_fields, allow_access, share_with_anyone


def check_google_credentials() -> None:
    print(FormatText.wait("Checking google credentials..."))
    if not FilePath.SHEETS_CREDENTIALS.exists():
        log = f'Sheets credential file "{FilePath.SHEETS_CREDENTIALS}" was not found.'
        log += " You will need to log on by clicking on this following link"
        log += " and pasting the code from browser."
        print(FormatText.warning(log))
    try:
        get_google_client()
        print(FormatText.success("Google authorization was successful."))
    except Exception as error:
        log = "Google authorization failed!"
        log += " Did you forget to provide the correct credentials.json file?"
        raise pygs.AuthenticationError(FormatText.error(log)) from error


def check_routine_sheet() -> None:
    get_spreadsheet(state.info[InfoField.ROUTINE_SHEET_ID])
    
def check_student_tutor_sheet() -> None:
    if state.info[InfoField.ST_SHEET_ID]:
        get_spreadsheet(state.info[InfoField.ST_SHEET_ID])

def check_enrolment_sheet() -> None:
    # enrolment id may be empty
    if enrolment_id := state.info[InfoField.ENROLMENT_SHEET_ID]:
        enrolment_sheet = get_spreadsheet(enrolment_id)
    else:
        # enrolment id not found -> create a new sheet
        log = f"Enrolment sheet ID is not specified {FilePath.INFO_TOML} file."
        log += " Creating a new spreadsheet..."
        print(FormatText.warning(log))
        spreadsheet_title = EnrolmentSprdsht.TITLE.format(
            course_code = state.info[InfoField.COURSE_CODE],
            semester = state.info[InfoField.SEMESTER],
        )
        enrolment_sheet = copy_spreadsheet(
            template_id=TemplateLink.ENROLMENT_SHEET,
            title=spreadsheet_title,
            folder_id=state.info[InfoField.MARKS_FOLDER_ID],
        )
    # finally update info file
    update_info_key(InfoField.ENROLMENT_SHEET_ID, enrolment_sheet.id)
    # update routines and stuff (for both new and old enrolment sheet)
    update_cells_from_fields(
        enrolment_sheet,
        {EnrolmentSprdsht.Meta.TITLE: EnrolmentSprdsht.Meta.FIELDS_TO_CELLS_DICT},
    )
    allow_access(enrolment_sheet.id, state.info[InfoField.ROUTINE_SHEET_ID])
    allow_access(enrolment_sheet.id, state.info[InfoField.ST_SHEET_ID])
    share_with_anyone(enrolment_sheet)  # also gives it some time to fetch marks groups