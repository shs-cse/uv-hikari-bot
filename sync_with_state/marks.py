import hikari
import pandas as pd
from bot_environment import state
from bot_environment.config import InfoKey, MarksSprdsht, SpecialChars, EnrolmentSprdsht, MarksDf
from wrappers.pygs import get_sheet_data
from wrappers.utils import FormatText


def update_marks_data(sec: int) -> None:
    df = get_sheet_data(
        state.info[InfoKey.MARKS_SHEET_IDS][str(sec)],
        MarksSprdsht.SecXX.TITLE.format(sec),
        start=MarksSprdsht.SecXX.HEADER_START_CELL,
    )
    df = df.set_index(MarksSprdsht.SecXX.STUDENT_ID_COL)
    is_col_published = df.iloc[MarksDf.ROW_NUM_PUBLISH_STATUS] == 1
    df = df.loc[:, is_col_published]
    df.columns = get_unique_headers(df)
    state.published_marks[sec] = df


# make the column headers unique
def get_unique_headers(df: pd.DataFrame) -> list[str]:
    # TODO: change props_df.iloc[..] to func args
    props_rows = [
        MarksDf.ROW_NUM_IS_UNIQUE,
        MarksDf.ROW_NUM_PARENT_COL,
        MarksDf.ROW_NUM_THIS_COL,
    ]
    props_df = df.iloc[props_rows]
    col_num_to_header = dict(zip(props_df.iloc[2], props_df.columns))
    for col in props_df.columns:
        is_unique = props_df[col].iloc[0]
        if is_unique != 1:
            parent_col_num = props_df[col].iloc[1]
            parent_header = col_num_to_header[parent_col_num]
            this_col_num = props_df[col].iloc[2]
            new_header = f"{parent_header}{SpecialChars.PARENT_CHILD_CHAR}{col}"
            col_num_to_header[this_col_num] = new_header
    return col_num_to_header.values()


def fetch_marks(student_id: int, assessment: str, sec: int = 0) -> pd.DataFrame | None:
    if not sec:
        sec = int(state.students[EnrolmentSprdsht.Students.MARKS_SEC_COL].loc[student_id])
    marks_df = state.published_marks[sec]
    if student_id not in marks_df.index:
        log = f"Section {sec:02d} published marks sheet"
        log += f" does not contain the student id: {student_id})"
        print(FormatText.warning(log))
        return
    if assessment not in marks_df.columns:
        log = f"Section {sec:02d} published marks sheet (for {student_id})"
        log += f" does not contain the assessment:\n\t{assessment}"
        print(FormatText.warning(log))
        return
    this_col_row = MarksDf.ROW_NUM_THIS_COL
    parent_col_row = MarksDf.ROW_NUM_PARENT_COL
    col_num = marks_df[assessment].iloc[this_col_row]
    cols = marks_df.iloc[parent_col_row] == col_num
    cols |= marks_df.iloc[this_col_row] == col_num
    rows = [MarksSprdsht.SecXX.STUDENT_ID_COL, student_id]  # Total rows have index 'Student Id'
    marks_df = marks_df.loc[rows, cols]
    marks_df.index = MarksDf.Student.INDEX
    return marks_df


def get_marks_out_of(earned_marks: int | str, total_marks: int | str, dummy_url: str) -> str:
    if isinstance(total_marks, int):
        if not earned_marks:
            earned_marks = SpecialChars.NOT_ATTENDED_CHAR
        text = f"[**{earned_marks}**]({dummy_url})"
        text += f"{SpecialChars.WIDE_SPACE}*out of*{SpecialChars.WIDE_SPACE}"
        text += f"{total_marks}"
    else:  # likely text data, print as it is
        text = f"{earned_marks} {total_marks}"
    return text


def display_marks(
    student_id: int, student_name: str, marks_df: pd.DataFrame, dummy_url: str
) -> hikari.Embed:
    embed = hikari.Embed()
    embed.color = 0xFF051A
    # assessment marks
    assessment = marks_df.columns[0]
    total_marks = marks_df.loc[MarksDf.Student.TOTAL_MARKS].loc[assessment]
    earned_marks = marks_df.loc[MarksDf.Student.EARNED_MARKS].loc[assessment]
    embed.description = f"## {assessment}\n## {SpecialChars.ZERO_WIDTH}{SpecialChars.WIDE_SPACE}"
    embed.description += get_marks_out_of(earned_marks, total_marks, dummy_url)
    # children marks
    for col in marks_df.columns[1:]:
        child_total_marks = marks_df.loc[MarksDf.Student.TOTAL_MARKS].loc[col]
        child_earned_marks = marks_df.loc[MarksDf.Student.EARNED_MARKS].loc[col]
        name = col.split(SpecialChars.PARENT_CHILD_CHAR)[-1]
        value = get_marks_out_of(child_earned_marks, child_total_marks, dummy_url)
        if not value.strip():
            continue
        value = f"{SpecialChars.ZERO_WIDTH}{2 * SpecialChars.WIDE_SPACE}{value}"
        embed.add_field(name, value)
    # add footer (optional)
    embed.set_footer(
        text=f"{student_id}{SpecialChars.WIDE_SPACE}{student_name}", icon=hikari.UnicodeEmoji("#️⃣")
    )
    return embed
