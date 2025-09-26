import tomlkit, re

from bot_environment.config import FilePath, InfoField, RegexPattern
from bot_environment import state
from setup_validation.google_sheets import check_google_credentials
from wrappers.utils import FormatText, update_info_key


def has_info_passed_before() -> bool:
    valid_toml_path = FilePath.VALID_TOML
    if not valid_toml_path.exists():
        return False
    with open(valid_toml_path) as fp:
        passed = tomlkit.load(fp)
        # matches all values with previously passed toml
        if all(state.info[key] == passed[key] for key in state.info):
            log = "Check complete! Values match previously passed valid toml."
            print(FormatText.success(log))
            # update valid toml file (e.g. comments)
            tomlkit.dump(state.info, fp)
            return True
    # mismatch -> needs checking each field
    print(FormatText.warning("Needs checking every json input field..."))
    # remove valid file
    valid_toml_path.unlink()
    return False


def check_and_load_info() -> None:
    check_google_credentials()
    with open(FilePath.INFO_TOML) as fp:
        state.info = tomlkit.load(fp)
    if not has_info_passed_before():
        check_info_keys()
        check_regex_patterns()
        ...


# check if info file contains all the fields
def check_info_keys() -> None:
    for attr, key in vars(InfoField).items():
        # skip private variables/attributes
        if attr.startswith("_"):
            continue
        # check if every fieldname exists in info
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
