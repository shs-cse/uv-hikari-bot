from hikari import Permissions
from pathlib import Path


# a.k.a ECT-BC Server for faculty information
class FacultyGuild:
    Id = 815535685959811083


class SpecialChars:
    WIDE_SPACE = "\u2001"
    ELLIPSIS_CHAR = "\u2026"
    # ZERO_WIDTH_SPACE = "\u200b"
    # ONE_CHAR_WIDTH_SPACE = "\u3000"


class ClassType:
    _IS_SUBCLASSED = True
    THEORY = "theory"
    LAB = "lab"
    LAB_A = "lab_a"
    LAB_B = "lab_b"
    if _IS_SUBCLASSED:
        ALL = [THEORY, LAB_A, LAB_B]
    else:
        ALL = [THEORY, LAB]

    def from_lab_suffix(lab_section: str) -> str:
        match lab_section:
            case "A":
                return ClassType.LAB_A
            case "B":
                return ClassType.LAB_B
            case _:
                return ClassType.LAB


class InfoKey:
    COURSE_CODE = "course_code"
    COURSE_NAME = "course_title"
    SEMESTER = "semester"
    LAST_SECTION = "last_section"
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


class FilePath:
    GOOGLE_CREDENTIALS = Path("google_credentials.json")
    SHEETS_CREDENTIALS = Path("sheets.googleapis.com-python.json")
    INFO_TOML = Path("info.toml")
    VALID_TOML = Path("info_valid.toml")


class PluginFileName:
    COMMANDS_FOLDER = "bot_commands"
    EVENTS_FOLDER = "bot_events"
    DEBUG_COMMANDS_FOLDER = "bot_commands_debug"


class TemplateLink:
    GUILD = "https://discord.new/pQ2GPFUGSjTB"
    ENROLMENT_SHEET = "1kKEFmMUYA0yelRp4V70unu2VB6hBXrezSynNJAmQK48"
    MARKS_SHEET = "1KdZeFEalvWJtOxvCzUcqqVw_L3IBlsQjys97fKC3n-c"


class RegexPattern:
    # email address
    EMAIL_ADDRESS = r"^((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$"
    # course details
    COURSE_CODE = r"CSE[0-9]{3}"
    COURSE_NAME = r"(?!<).+"
    SEMESTER = r"(Fall|Spring|Summer)'[0-9]{2}"
    # student details
    STUDENT_ID = r"^([0-9]{8}|[0-9]{10})$"
    STUDENT_NICKNAME = r"\[[0-9]{8,10}\].+"
    # faculty details
    FACULTY_NICKNAME = r"^\[([A-Z0-9]{3,5})\].+"
    # google drive file/folder id
    GOOGLE_DRIVE_LINK_ID = r"(?<=/)[\w_-]{15,}|^[\w_-]{15,}"
    ST_SHEET_ID = r"^$|" + GOOGLE_DRIVE_LINK_ID
    # discord id
    DISCORD_ID = r"[0-9]{17,19}"
    DISCORD_BOT_TOKEN = r"^.{25,}$"  # discord keeps changing this...
    # DISCORD_BOT_TOKEN = r'^([MN][\w-]{23,25})\.([\w-]{6})\.([\w-]{27,39})$'


# all special channel names in this guild
class ChannelName:
    WELCOME = "👏🏻welcome✌🏻"
    ADMIN_HELP = "💁🏻admin-help"
    GENERAL_ANNOUNCEMENT = "📣general-announcements"
    if ClassType._IS_SUBCLASSED:
        SECTION_CATEGORY = {
            ClassType.THEORY: SpecialChars.WIDE_SPACE.join(("Section", "{:02d}", "Theory")),
            ClassType.LAB_A: SpecialChars.WIDE_SPACE.join(("Section", "{:02d} A", "Lab")),
            ClassType.LAB_B: SpecialChars.WIDE_SPACE.join(("Section", "{:02d} B", "Lab")),
        }
    else:  # TODO: change below, currently set like this for old servers
        SECTION_CATEGORY = {
            ClassType.THEORY: "SECTION {:02d} THEORY",
            ClassType.LAB: "SECTION {:02d} LAB",
        }


# all special role names in this guild
class RoleName:
    ADMIN = "admin"
    BOT_ADMIN = "bot-admin"
    BOT = "bot"
    FACULTY = "faculty"
    THEORY_FACULTY = "theory-faculty"
    LAB_FACULTY = "lab-faculty"
    STUDENT_TUTOR = "student-tutor"
    STUDENT = "student"
    if ClassType._IS_SUBCLASSED:
        SECTION = {
            ClassType.THEORY: "sec-{:02d}",
            ClassType.LAB_A: "sec-{:02d}A-lab",
            ClassType.LAB_B: "sec-{:02d}B-lab",
        }
    else:
        SECTION = {
            ClassType.THEORY: "sec-{:02d}",
            ClassType.LAB: "sec-{:02d}-lab",
        }


class DisplayName:
    STUDENT = "[{}] {}"
    STUDENT_TUTOR = "[ST-{}] {}"

    def fmt(template: str, *args: tuple) -> str:
        disp = template.format(*args)
        if len(disp) <= 32:
            return disp
        return disp[:31] + SpecialChars.ELLIPSIS_CHAR


class EnrolmentSprdsht:
    TITLE = "{course_code} {semester} Enrolment Manager"

    class Meta:
        TITLE = "Meta"
        KEYS_AT_CELLS_DICT = {  # write data to cell
            "B1": InfoKey.SEMESTER,
            "B2": InfoKey.COURSE_CODE,
            "B3": InfoKey.COURSE_NAME,
            "B4": InfoKey.LAST_SECTION,
            "B5": InfoKey.MISSING_SECTIONS,
            "B7": InfoKey.ROUTINE_SHEET_ID,
            "B11": InfoKey.ST_SHEET_ID,
        }
        KEYS_FROM_CELLS_DICT = {  # read data from cell
            InfoKey.MARKS_GROUPS: "B14"  # fmt:skip
        }

    class Students:
        TITLE = "Students"
        STUDENT_ID_COL = "Student Id"
        NAME_COL = "Name"
        THEORY_SECTION_COL = "Theory Section"
        LAB_SECTION_COL = "Lab Section"
        ADVISING_DISCORD_ID_COL = "Discord Id (Adv. Verified)"
        DISCORD_ID_COL = "Discord Id"
        MARKS_SEC_COL = "Marks Section"
        DF_DTYPE = {
            STUDENT_ID_COL: int,
            NAME_COL: str,
            THEORY_SECTION_COL: int,
            LAB_SECTION_COL: str,
            ADVISING_DISCORD_ID_COL: str,
            DISCORD_ID_COL: str,
            MARKS_SEC_COL: int,
        }

    class Routine:
        TITLE = "Routine"
        SECTION_COL = "Section"
        FACULTY_COL = {
            ClassType.THEORY: "Theory Faculty",
            ClassType.LAB: "Lab Faculty",
        }
        THEORY_SECTION_COL = "Theory Section"
        ST_INITIAL_COL = "Student Tutor Initial"
        ST_ID_COL = "Student Tutor Id"
        ST_NAME_COL = "Student Tutor Name"

    class Connect:
        TITLE = "Connect"
        RANGE = "A1"

    class Discord:
        TITLE = "Discord"
        RANGE = "B2:E"


class MarksSprdsht:
    TITLE = "{course_code}-{sections} Marks Gradesheet {semester}"

    class Meta:
        TITLE = "Meta"
        KEYS_AT_CELLS_DICT = {"K2": InfoKey.ENROLMENT_SHEET_ID}

    class SecXX:
        TITLE = "Sec {:02d}"
        COL_FOR_STUDENT_IDS = 2
        ROW_FOR_HEADER = 3
        HEADER_START = (ROW_FOR_HEADER, COL_FOR_STUDENT_IDS)
        # TODO: rename
        ACTUAL_ROW_DATA_START = 100
        # TODO: remove -(1+ROW_FOR_HEADER)
        ROW_FOR_PUBLISH_STATUS = 24 - (1 + ROW_FOR_HEADER)
        ROW_FOR_THIS_COL = 14 - (1 + ROW_FOR_HEADER)
        ROW_FOR_ALL_CHILDREN = 17 - (1 + ROW_FOR_HEADER)
        ROW_DATA_START = 100 - (1 + ROW_FOR_HEADER)
