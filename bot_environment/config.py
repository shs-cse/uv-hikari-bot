from hikari import Permissions
from pathlib import Path


# a.k.a ECT-BC Server for faculty information
class FacultyGuild:
    Id = 815535685959811083


class SpecialChars:
    ZERO_WIDTH_SPACE = "\u200b"
    ONE_CHAR_WIDTH_SPACE = "\u3000"


class ClassType:
    THEORY = "theory"
    LAB_A = "lab_a"
    LAB_B = "lab_b"
    ALL = [THEORY, LAB_A, LAB_B]


class InfoField:
    COURSE_CODE = "course_code"
    COURSE_NAME = "course_title"
    SEMESTER = "semester"
    NUM_SECTIONS = "last_section"
    MISSING_SECTIONS = "missing_sections"
    # tokens and ids
    MARKS_FOLDER_ID = "enrolment_and_marks_folder_id"
    ROUTINE_SHEET_ID = "routine_sheet_id"
    ST_SHEET_ID = "student_tutor_sheet_id"
    # ST_SHEET_ID = "st_sheet_id"
    GUILD_ID = "discord_server_id"
    BOT_TOKEN = "discord_bot_token"
    # auto-generated fields
    INVITE_LINK = "discord_invite_link"
    ENROLMENT_SHEET_ID = "enrolment_sheet_id"
    MARKS_ENABLED = "marks_enabled"
    MARKS_GROUPS = "marks_groups"
    MARKS_SHEET_IDS = "marks_sheet_ids"


class RolePermissions:
    STUDENT_TUTOR = Permissions.PRIORITY_SPEAKER
    FACULTY = STUDENT_TUTOR | Permissions.MANAGE_MESSAGES | Permissions.MODERATE_MEMBERS
    BOT_ADMIN = FACULTY | Permissions.MANAGE_GUILD
    ADMIN = BOT_ADMIN | Permissions.ADMINISTRATOR


# class FileName:
#     GOOGLE_CREDENTIALS = "google_credentials.json"
#     SHEETS_CREDENTIALS = "sheets.googleapis.com-python.json"
#     INFO_TOML = "info.toml"
#     VALID_TOML = "info_valid.toml"
#     COMMANDS_FOLDER = "bot_commands"
#     EVENTS_FOLDER = "bot_events"
#     BULK_DELETE = f"{COMMANDS_FOLDER}.bulk_delete"
#     # DISCORD_WRAPPER = "wrappers.discord"
#     # DISCORD_SECTION_VALIDATION = "setup_validation.discord_sec"
    

class FilePath:
    GOOGLE_CREDENTIALS = Path("google_credentials.json")
    SHEETS_CREDENTIALS = Path("sheets.googleapis.com-python.json")
    INFO_TOML = Path("info.toml")
    VALID_TOML = Path("info_valid.toml")
    COMMANDS_FOLDER = Path("bot_commands")
    EVENTS_FOLDER = Path("bot_events")
    BULK_DELETE = Path(f"{COMMANDS_FOLDER}.bulk_delete")
    # DISCORD_WRAPPER = Path("wrappers.discord")
    # DISCORD_SECTION_VALIDATION = Path("setup_validation.discord_sec")


class TemplateLink:  # TODO: plural to singular (TemplateLink)
    GUILD = "https://discord.new/RVh3qBrGcsxA"
    ENROLMENT_SHEET = "1NUMv5gDhDoZWmL-PyHsNawquZKY2FXVb8hai7nSh6CY"
    MARKS_SHEET = "1SqQkkIbbsnSGcAbQ8si3UfitUs6b-cFTJ8fit9UoWp8"


class RegexPattern:
    # email address
    EMAIL_ADDRESS = r"^((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$"
    # course details
    COURSE_CODE = r"CSE[0-9]{3}"
    COURSE_NAME = r"(?!<).+"
    SEMESTER = r"(Fall|Spring|Summer) 20[0-9]{2}"
    # student details
    STUDENT_ID = r"([0-9]{8}|[0-9]{10})"
    STUDENT_NICKNAME = r"\[[0-9]{8,10}\].+"
    # faculty details
    FACULTY_NICKNAME = r"^\[([A-Z0-9]{3,5})\].+"
    # google drive file/folder id
    GOOGLE_DRIVE_LINK_ID = r"(?<=/)[\w_-]{15,}|^[\w_-]{15,}"
    # discord id
    DISCORD_ID = r"[0-9]{17,19}"
    DISCORD_BOT_TOKEN = r"^\w{25,}$" # discord keeps changing this...
    # DISCORD_BOT_TOKEN = r'^([MN][\w-]{23,25})\.([\w-]{6})\.([\w-]{27,39})$' 
