import hikari, miru, tomlkit
import pandas as pd
from bot_environment.config import ClassType
from wrappers.discord import DiscordClassTypeTemplate
# from wrappers.pygs import Spreadsheet

miru_client: miru.Client | None = None

info: tomlkit.TOMLDocument | None = None

# enrolment: Spreadsheet | None = None
routine: pd.DataFrame = pd.DataFrame()
students: pd.DataFrame = pd.DataFrame()
available_secs: list = []

# guild related objects
guild: hikari.Guild | None = None
eee_guild: hikari.Guild | None = None

# role related objects
sec_roles: dict[int, dict[ClassType, hikari.Role]] = {}
# e.g. sec_roles = {1: {'theory': @sec-01, 'lab_a': @sec-01A-lab,  'lab_b': @sec-01B-lab, }, ...}
all_sec_roles: set = {}
# e.g. all_sec_roles = {@sec-01, @sec-01A-lab, @sec-01B-lab, ...}
faculty_role: hikari.Role | None = None
faculty_sub_roles: dict[ClassType, hikari.Role] = {}
st_role: hikari.Role | None = None
admin_role: hikari.Role | None = None
bot_admin_role: hikari.Role | None = None
student_role: hikari.Role | None = None

# discord sec channels
sec_template: dict[ClassType, DiscordClassTypeTemplate] = {}

# marks stuff
published_marks: dict[int, pd.DataFrame] = {}
