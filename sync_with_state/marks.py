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
    # assessment and its children
    this_col_row = MarksDf.ROW_NUM_THIS_COL
    parent_col_row = MarksDf.ROW_NUM_PARENT_COL
    col_num = marks_df[assessment].iloc[this_col_row]
    cols = marks_df.iloc[parent_col_row] == col_num
    cols |= marks_df.iloc[this_col_row] == col_num
    # total (bonus and actual), student marks (bonus and actual) and children
    rows = marks_df.index.get_loc(MarksSprdsht.SecXX.STUDENT_ID_COL)  # total row's index
    rows |= marks_df.index.get_loc(student_id)
    rows[MarksDf.ROW_NUM_NUMERIC_CHILDREN_COL] = True
    marks_df = marks_df.loc[rows, cols]
    marks_df.index = MarksDf.Single.INDEX
    return marks_df
