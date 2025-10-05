import tomlkit, re

from bot_environment.config import FilePath, InfoField, RegexPattern
from bot_environment import state
from setup_validation.google_sheets import check_google_credentials, check_enrolment_sheet
from setup_validation.google_sheets import check_routine_sheet, check_student_tutor_sheet
from setup_validation.marks import check_marks_enabled, check_marks_groups_and_sheets
from setup_validation.marks import load_marks_sections
from sync_with_state.sheets import pull_from_enrolment, push_marks_section_to_enrolment
from wrappers.utils import FormatText, update_info_key


def has_info_passed_before() -> bool:
    if not FilePath.VALID_TOML.exists():
        return False
    with open(FilePath.VALID_TOML) as fp:
        passed = tomlkit.load(fp)
    # matches all values with previously passed toml file
    if all(state.info[key] == passed[key] for key in state.info):
        log = "Check complete! Values match previously passed valid toml."
        print(FormatText.success(log))
        # update valid toml file (e.g. comments)
        with open(FilePath.VALID_TOML, 'w') as fp:
            tomlkit.dump(state.info, fp)
        return True
    # mismatch -> needs checking each field
    print(FormatText.warning("Needs checking every json input field..."))
    # remove valid file
    FilePath.VALID_TOML.unlink()
    return False


def check_and_load_info() -> None:
    check_google_credentials()
    with open(FilePath.INFO_TOML) as fp:
        state.info = tomlkit.load(fp)
    if not has_info_passed_before():
        check_info_keys()
        check_regex_patterns()
        check_and_load_sections()
        check_marks_enabled()
        check_routine_sheet()
        check_student_tutor_sheet()
        check_enrolment_sheet()
        check_marks_groups_and_sheets()
        # create valid toml file
        with open(FilePath.VALID_TOML, 'w') as fp:
            tomlkit.dump(state.info, fp)
    # always load after checked
    load_sections()
    pull_from_enrolment()
    load_marks_sections()
    push_marks_section_to_enrolment()
    

# check functions may access state but can't update it
# check if info file contains all the fields
def check_info_keys() -> None:
    for attr, key in vars(InfoField).items():
        # skip private variables/attributes
        if attr.startswith("_"):
            continue
        # check if every toml key exists in info file
        if key not in state.info:
            log = f'{FilePath.INFO_TOML} file does not contain the key: "{key}".'
            raise LookupError(FormatText.error(log))
    # passed all field checks
    log = f"{FilePath.INFO_TOML} file contains all the necessary keys."
    print(FormatText.success(log))



# check if info values matches proper regex
def check_regex_patterns() -> None:
    keys_and_regex_patterns = {
        InfoField.COURSE_CODE: RegexPattern.COURSE_CODE,
        InfoField.COURSE_NAME: RegexPattern.COURSE_NAME,
        InfoField.SEMESTER: RegexPattern.SEMESTER,
        InfoField.ROUTINE_SHEET_ID: RegexPattern.GOOGLE_DRIVE_LINK_ID,
        InfoField.ST_SHEET_ID: RegexPattern.GOOGLE_DRIVE_LINK_ID,
        InfoField.MARKS_FOLDER_ID: RegexPattern.GOOGLE_DRIVE_LINK_ID,
        InfoField.GUILD_ID: RegexPattern.DISCORD_ID,
        InfoField.BOT_TOKEN: RegexPattern.DISCORD_BOT_TOKEN,
    }
    # check each of the fields in a loop
    for key, pattern in keys_and_regex_patterns.items():
        log = f'{FilePath.INFO_TOML} > "{key}": '
        extracted = re.search(pattern, state.info[key])
        if not extracted:
            log += rf'"{state.info[key]}" does not match expected pattern: "{pattern}".'
            raise ValueError(FormatText.error(log))
        # update if not exact match (e.g. full link -> id only)
        update_info_key(key, extracted[0])
        log += FormatText.bold(extracted[0])
        print(FormatText.status(log))
    # validated all regex checks
    log = f"Course details regex checks out in {FilePath.INFO_TOML} file."
    print(FormatText.success(log))


# check number of sections and missing sections
def check_and_load_sections() -> None:
    last_sec = state.info[InfoField.NUM_SECTIONS]
    missing_secs = state.info[InfoField.MISSING_SECTIONS]
    # make sure positive
    if last_sec <= 0:
        log = "Last section must be a positive integer."
        raise ValueError(FormatText.error(log))
    # check missing sections
    if missing_secs:
        if not set(missing_secs).issubset(range(1, last_sec)):
            log = "Missing sections that don't exist."
            log += " Keep in mind, the last section cannot be missing."
            log += " Change the last section input instead."
            raise ValueError(FormatText.error(log))
    # passed all checks
    load_sections()
    log = "Number of sections and missing sections seems ok."
    print(FormatText.success(log))
    
    
def load_sections() -> None:
    # list of available sections (integers)
    state.available_secs = [
        sec for sec in range(1, state.info[InfoField.NUM_SECTIONS]+1)
        if sec not in state.info[InfoField.MISSING_SECTIONS]
    ]
    log = FormatText.bold(state.available_secs)
    print(FormatText.status(f"Available Sections: {log}"))