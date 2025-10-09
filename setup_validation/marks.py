import json
from bot_environment import state
from bot_environment.config import InfoKey, EnrolmentSprdsht, MarksSprdsht, TemplateLink
from sync_with_state.sheets import update_student_list, push_marks_section_to_enrolment
from wrappers.utils import FormatText, update_info_key
from wrappers.pygs import Spreadsheet, Worksheet, WorksheetNotFound
from wrappers.pygs import get_spreadsheet, copy_spreadsheet, get_sheet_by_name
from wrappers.pygs import update_cells_from_keys
from wrappers.pygs import share_with_faculty_as_editor


# check if marks_enabled has boolean values or not
def check_marks_enabled() -> None:
    if not isinstance(state.info[InfoKey.MARKS_ENABLED], bool):
        log = "Marks enabled must be a boolean value"
        raise TypeError(FormatText.error(log))
    # validated marks enabled
    log = "enabled" if state.info[InfoKey.MARKS_ENABLED] else "disabled"
    print(FormatText.success(f"Marks spreadsheets are {log} for all sections."))


def check_marks_groups_and_sheets() -> None:
    if not state.info[InfoKey.MARKS_ENABLED]:
        print(FormatText.status("Marks feature is disabled."))
        return
    # fetch marks groups from enrolment and check spreadsheets
    check_marks_groups(state.info[InfoKey.ENROLMENT_SHEET_ID])
    for email, marks_group in state.info[InfoKey.MARKS_GROUPS].items():
        for section in marks_group:
            check_marks_sheet(section, email, marks_group)


def check_marks_groups(enrolment_sheet: Spreadsheet) -> None:
    print(FormatText.wait(f'Fetching "{InfoKey.MARKS_GROUPS}" from spreadsheet...'))
    meta_wrksht = get_sheet_by_name(enrolment_sheet, EnrolmentSprdsht.Meta.TITLE)
    marks_groups_cell = EnrolmentSprdsht.Meta.KEYS_FROM_CELLS_DICT[InfoKey.MARKS_GROUPS]
    marks_groups_str: str = meta_wrksht.get_value(marks_groups_cell)
    marks_groups: dict[str, list[int]] = json.loads(marks_groups_str)
    print(FormatText.status(f'"{InfoKey.MARKS_GROUPS}": {FormatText.bold(marks_groups)}'))
    # check if all sections in marks groups
    if set(state.available_secs) != {sec for group in marks_groups.values() for sec in group}:
        log = "Marks groups contain sections that does not exist in"
        log += f" {meta_wrksht.url}&range={marks_groups_cell}"
        raise ValueError(FormatText.error(log))
    # update info toml
    update_info_key(InfoKey.MARKS_GROUPS, marks_groups)


def check_marks_sheet(sec: int, email: str, group: list[int]) -> Worksheet:
    marks_ids = state.info[InfoKey.MARKS_SHEET_IDS].copy()  # TODO: why copy?
    # fetch or create spreadsheet
    if marks_ids.get(str(sec), ""):  # key may not exist or value may be ""
        spreadsheet = get_spreadsheet(marks_ids[str(sec)])
    elif sec == group[0]:  # new spreadsheet if first sec in group
        spreadsheet = create_marks_spreadsheet(sec, group, email)
    else:  # first group member has spreadsheet
        spreadsheet = get_spreadsheet(marks_ids[str(group[0])])
    marks_ids[str(sec)] = spreadsheet.id
    update_info_key(InfoKey.MARKS_SHEET_IDS, marks_ids)
    log = f'Section {sec:02d} > Marks spreadsheet: "{spreadsheet.title}"'
    print(FormatText.success(log))
    return get_or_create_marks_worksheet(spreadsheet, sec)


# create a spreadsheet that will contain marks for several sections
def create_marks_spreadsheet(sec: int, group: list[int], email: str) -> Spreadsheet:
    print(FormatText.warning(f"Creating new spreadsheet for section {sec:02d}..."))
    spreadsheet = copy_spreadsheet(
        TemplateLink.MARKS_SHEET,
        MarksSprdsht.TITLE.format(
            course_code=state.info[InfoKey.COURSE_CODE],
            sections=",".join(f"{s:02d}" for s in group),
            semester=state.info[InfoKey.SEMESTER],
        ),
        state.info[InfoKey.MARKS_FOLDER_ID],
    )
    share_with_faculty_as_editor(spreadsheet, email)
    update_cells_from_keys(
        spreadsheet, {MarksSprdsht.Meta.TITLE: MarksSprdsht.Meta.KEYS_AT_CELLS_DICT}
    )
    return spreadsheet


# create a worksheet for the section marks in spreadsheet
def get_or_create_marks_worksheet(spreadsheet: Spreadsheet, sec: int) -> Worksheet:
    try:  # success -> sec worksheet already exists
        sec_sheet = get_sheet_by_name(spreadsheet, MarksSprdsht.SecXX.TITLE.format(sec))
    except WorksheetNotFound:
        # fail -> sec worksheet does not exist
        print(FormatText.status("Creating new worksheet..."))
        template_sheet = get_sheet_by_name(spreadsheet, MarksSprdsht.SecXX.TITLE.format(0))
        sec_sheet: Worksheet = template_sheet.copy_to(spreadsheet.id)  # type:ignore
        sec_sheet.hidden = False
        sec_sheet.title = MarksSprdsht.SecXX.TITLE.format(sec)
        populate_marks_worksheet_with_student_id(sec_sheet, sec)
    return sec_sheet


def populate_marks_worksheet_with_student_id(sec_sheet: Worksheet, sec: int) -> None:
    update_student_list()
    if state.students.empty:
        log = "Can't populate because no student in Enrolment sheet."
        log += " (at least no student in local data `state.students`)"
        print(FormatText.status(log))
        return
    start_cell = MarksSprdsht.SecXX.MARKS_DATA_START_CELL
    end_cell = (sec_sheet.rows, MarksSprdsht.SecXX.COL_NUM_STUDENT_IDS)
    student_ids = sec_sheet.get_as_df(start=start_cell, end=end_cell)
    # populate with student ids only if marks sheet is empty
    if not student_ids.empty:
        log = "Marks sheet already contains student id(s)."
        log += " Can't populate due to risk of overwriting marks."
        print(FormatText.status(log))
        return
    # filter students in section and populate marks sheet
    print(FormatText.status(f"Populating marks sheet for section {sec:02d} with student list..."))
    is_student_in_sec = state.students[EnrolmentSprdsht.Students.THEORY_SECTION_COL] == sec
    sec_students = state.students[is_student_in_sec]
    sec_sheet.set_dataframe(
        sec_students[[EnrolmentSprdsht.Students.NAME_COL, EnrolmentSprdsht.Students.GSUITE_COL]],
        start=start_cell,
        copy_index=True,
    )


def load_marks_sections() -> None:
    if not state.info[InfoKey.MARKS_ENABLED]:
        return
    # refresh all marks section column entry
    state.students[EnrolmentSprdsht.Students.MARKS_SEC_COL] = 0
    for sec in state.available_secs:
        load_marks_section(sec)


def load_marks_section(marks_sec: int) -> None:
    for email, group in state.info["marks_groups"].items():
        if marks_sec in group:
            break
    sec_sheet = check_marks_sheet(marks_sec, email, group)
    # update both in state.students and enrolment
    if state.students.empty:
        return
    start_cell = MarksSprdsht.SecXX.MARKS_DATA_START_CELL
    end_cell = (sec_sheet.rows, MarksSprdsht.SecXX.COL_NUM_STUDENT_IDS)
    student_ids = sec_sheet.get_as_df(start=start_cell, end=end_cell)
    if student_ids.empty:
        return
    # update marks section in state.students
    print(FormatText.wait(f"Updating student's marks section for section {marks_sec:02d} sheet..."))
    is_student_in_sec_sheet = state.students.index.isin(student_ids.iloc[:, 0])
    state.students.loc[is_student_in_sec_sheet, EnrolmentSprdsht.Students.MARKS_SEC_COL] = marks_sec
    print(FormatText.status("Updated marks section in students dataframe."))
    # also update marks section in enrolment sheet
    push_marks_section_to_enrolment()
    print(FormatText.success(f"Updated student's marks section for section {marks_sec:02d} sheet."))
