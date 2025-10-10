import hikari, crescent, re
from miru.ext import nav
import pandas as pd
from bot_environment import state
from bot_environment.config import MarksDf, SpecialChars, RegexPattern, EnrolmentSprdsht
from sync_with_state.marks import fetch_marks


def get_marks_out_of(earned_marks: int | str, total_marks: int | str) -> str:
    if isinstance(total_marks, int | float):
        if earned_marks == "":
            earned_marks = SpecialChars.NOT_ATTENDED_CHAR
        dummy_url = f"https://discord.com/channels/{state.guild.id}"
        text = f"[**{earned_marks}**]({dummy_url})"
        text += f"{SpecialChars.WIDE_SPACE}*out of*{SpecialChars.WIDE_SPACE}"
        text += f"{total_marks}"
    elif "out of" in total_marks:  # likely text data, but contains out of
        text = f"{earned_marks} {total_marks}"
    else:  # likely text data, print as it is
        text = f"{earned_marks}"
    return text


def create_marks_embed(student_id: int, student_name: str, marks_df: pd.DataFrame) -> hikari.Embed:
    embed = hikari.Embed()
    embed.color = 0xFF051A
    # assessment marks
    assessment = marks_df.columns[0]
    total_marks = marks_df.loc[MarksDf.Single.TOTAL_MARKS].loc[assessment]
    earned_marks = marks_df.loc[MarksDf.Single.EARNED_MARKS].loc[assessment]
    title = assessment.split(SpecialChars.PARENT_CHILD_CHAR)[-1]
    embed.description = f"## {title}\n## {SpecialChars.ZERO_WIDTH}{SpecialChars.WIDE_SPACE}"
    embed.description += get_marks_out_of(earned_marks, total_marks)
    # children marks
    for col in marks_df.columns[1:]:
        child_total_marks = marks_df.loc[MarksDf.Single.TOTAL_MARKS].loc[col]
        child_earned_marks = marks_df.loc[MarksDf.Single.EARNED_MARKS].loc[col]
        name = col.split(SpecialChars.PARENT_CHILD_CHAR)[-1]
        value = get_marks_out_of(child_earned_marks, child_total_marks)
        if 'Grace' in name and child_earned_marks == "" or child_earned_marks == 0:
            continue
        if not value.strip():
            continue
        value = f"{SpecialChars.ZERO_WIDTH}{2 * SpecialChars.WIDE_SPACE}{value}"
        embed.add_field(name, value)
    # add footer (optionally)
    embed.set_footer(
        text=f"{student_id}{SpecialChars.WIDE_SPACE}{student_name.title()}",
        icon=hikari.UnicodeEmoji("#️⃣"),
    )
    return embed


def create_marks_nav_page(
    student: hikari.Member,
    student_id: int,
    student_name: str,
    marks_df: pd.DataFrame,
) -> nav.Page:
    return nav.Page(
        content=f"{student.mention} Here is your requested marks details.",
        embed=create_marks_embed(student_id, student_name, marks_df),
    )


def create_marks_navigator(student: hikari.Member, assessment: str) -> nav.NavigatorView:
    if student.get_top_role() != state.student_role:
        log = f"Can't Fetch Marks: {student.display_name} is not a verified student."
        raise Exception(log)
    try:
        student_id = int(re.search(RegexPattern.MEMBER_INITIAL, student.display_name).group(1))
        student_name = state.students[EnrolmentSprdsht.Students.NAME_COL].loc[student_id]
        marks_sec = int(state.students[EnrolmentSprdsht.Students.MARKS_SEC_COL].loc[student_id])
    except Exception as err:
        log = f"Unable to find student details (id/name/sec): {student.mention}."
        raise Exception(log) from err
    marks_df = fetch_marks(student_id, assessment, marks_sec)
    if marks_df is None:
        log = "Marks is unpublished or Student was not found:"
        log += f" {marks_sec} > {student_id} > {assessment}."
        raise Exception(log)
    pages = [create_marks_nav_page(student, student_id, student_name, marks_df)]
    for col in marks_df.columns[1:]:
        if marks_df.loc[MarksDf.Single.CHILDREN, col]:
            child_df = fetch_marks(student_id, col, marks_sec)
            pages.append(create_marks_nav_page(student, student_id, student_name, child_df))
    navigator = nav.NavigatorView(pages=pages, timeout=10)
    return navigator
