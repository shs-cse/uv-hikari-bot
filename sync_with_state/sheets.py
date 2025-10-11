from bot_environment import state
from bot_environment.config import InfoKey, EnrolmentSprdsht
from wrappers.pygs import get_sheet_by_name, get_sheet_data, update_sheet_values
from wrappers.utils import FormatText


def pull_from_enrolment() -> None:
    print(FormatText.wait("Pulling data from enrolment sheet..."))
    update_routine()
    update_student_list()
    print(FormatText.success("Pulled data from enrolment sheet successfully."))


def push_to_enrolment() -> None:
    print(FormatText.wait("Pushing data to enrolment sheet..."))
    push_marks_section_to_enrolment()
    push_discord_data_to_enrolment()
    print(FormatText.success("Pushed data to enrolment sheet successfully."))


# fetch routine data from enrolment sheet
def update_routine() -> None:
    print(FormatText.wait("Updating routine dataframe..."))
    state.routine = get_sheet_data(
        state.info[InfoKey.ENROLMENT_SHEET_ID], EnrolmentSprdsht.Routine.TITLE
    )
    state.routine.set_index(EnrolmentSprdsht.Routine.SECTION_COL, inplace=True)
    print(FormatText.success("Updated routine dataframe successfully."))


def update_student_list() -> None:
    # fetch student list from
    print(FormatText.wait("Updating enrolled student list dataframe..."))
    state.students = get_sheet_data(
        state.info[InfoKey.ENROLMENT_SHEET_ID],
        EnrolmentSprdsht.Students.TITLE,
        numerize=False,
        empty_value=None,
    )
    for col, dtype in EnrolmentSprdsht.Students.DF_DTYPE.items():
        if dtype is int:  # to avoid df.astype raising errors with None
            state.students[col] = state.students[col].fillna(0)
    state.students = state.students.astype(EnrolmentSprdsht.Students.DF_DTYPE)
    state.students = state.students.set_index(EnrolmentSprdsht.Students.STUDENT_ID_COL)
    state.students = state.students[state.students.index > 0]
    print(FormatText.success("Updated enrolled student list dataframe successfully."))


def push_marks_section_to_enrolment() -> None:
    list_of_marks_sec = state.students[[EnrolmentSprdsht.Students.MARKS_SEC_COL]]
    list_of_marks_sec = list_of_marks_sec.fillna(0).to_numpy(int).tolist()
    students_sheet = get_sheet_by_name(
        state.info[InfoKey.ENROLMENT_SHEET_ID], EnrolmentSprdsht.Students.TITLE
    )
    ...  # TODO: make sure student list matches
    students_sheet_headers: list = students_sheet.get_row(1)
    marks_sec_col_num = 1 + students_sheet_headers.index(EnrolmentSprdsht.Students.MARKS_SEC_COL)
    marks_sec_start_cell = students_sheet.cell((2, marks_sec_col_num)).label
    update_sheet_values({marks_sec_start_cell: list_of_marks_sec}, students_sheet)
    print(FormatText.status("Updated marks section in enrolment sheet."))


def push_discord_data_to_enrolment() -> None:
    print(FormatText.status("Updating discord data in enrolment sheet..."))
    # clear old discord data
    discord_sheet = get_sheet_by_name(
        state.info[InfoKey.ENROLMENT_SHEET_ID], EnrolmentSprdsht.Discord.TITLE
    )
    discord_sheet.clear(EnrolmentSprdsht.Discord.RANGE)
    # extract member roles (just for visuals, not really mandatory anymore)
    data = []
    for mem_id, mem in state.guild.get_members().items():
        top_role_name = mem.get_top_role().name
        mem_roles = sorted(mem.get_roles(), key=lambda r: r.name)
        other_roles_names = ", ".join(
            role.name for role in mem_roles[1:] if role.name != top_role_name
        )
        data.append([str(mem_id), mem.display_name, top_role_name, other_roles_names])
    # dump discord data
    starting_cell = EnrolmentSprdsht.Discord.RANGE.split(":")[0]
    update_sheet_values({starting_cell: data}, discord_sheet)
    print(FormatText.status("Updated discord data in enrolment sheet successfully."))
