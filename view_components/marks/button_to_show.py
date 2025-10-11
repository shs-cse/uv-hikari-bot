import hikari, miru
from bot_environment import state
from bot_environment.config import SpecialChars, InfoKey, ClassType, MarksSprdsht
from wrappers.utils import FormatText, update_info_key
from view_components.marks.embed_and_nav import create_marks_navigator


def get_custom_id(section: int, assessment: str) -> str:
    # NOTE: be careful, custom id can be a max of 100 chars/bytes
    return f"{section}{SpecialChars.MARKS_BUTTON_ID_SEP}{assessment}"


class ShowMarksButton(miru.Button):
    def __init__(
        self,
        sec: int,
        assessment: str,
        label: str = "Show Marks",
        row: int | None = None,
        style: hikari.InteractiveButtonTypesT = hikari.ButtonStyle.DANGER,
    ) -> None:
        super().__init__(label=label, style=style, row=row, emoji="📝", autodefer=True)
        self.custom_id = get_custom_id(sec, assessment)
        self.assessment = assessment
        # update toml info if needed
        if assessment not in state.info[InfoKey.MARKS_BUTTONS][str(sec)]:
            all_custom_ids = state.info[InfoKey.MARKS_BUTTONS].copy()  # for comparison
            all_custom_ids[str(sec)] = [*all_custom_ids[str(sec)], assessment]  # NOTE: don't append
            update_info_key(InfoKey.MARKS_BUTTONS, all_custom_ids)

    async def callback(self, ctx: miru.ViewContext) -> None:
        # await ctx.defer(flags=hikari.MessageFlag.EPHEMERAL)
        if not state.info[InfoKey.MARKS_ENABLED]:
            log = "Marks feature is disabled. This command is currently unavailable."
            await ctx.respond(log, flags=hikari.MessageFlag.EPHEMERAL)
            return
        if ctx.member.get_top_role() != state.student_role:
            log = "Can't show marks because you are not a verified student."
            await ctx.respond(log, flags=hikari.MessageFlag.EPHEMERAL)
            return
        try:  # to actually show marks
            navigator = create_marks_navigator(ctx.member, self.assessment)
            builder = await navigator.build_response_async(state.miru_client, ephemeral=True)
            await ctx.respond_with_builder(builder)
            state.miru_client.start_view(navigator)
        except Exception as err:
            log = "Something went wrong, can't fetch marks:"
            log += f"\n```\n{err}```"
            print(FormatText.error(err))
            await ctx.respond(log, flags=hikari.MessageFlag.EPHEMERAL)


class ShowMarksView(miru.View):
    def __init__(self, sec: int, assessment: str, faculty_text: str = "") -> None:
        super().__init__(timeout=None)
        # post content
        sec_role = state.sec_roles[sec][ClassType.THEORY]
        assessment_title = assessment.split(SpecialChars.PARENT_CHILD_CHAR)[-1]
        assessment_is_grade = assessment_title == MarksSprdsht.SecXX.GRADE_COL
        if not assessment_is_grade:
            assessment_title = f"{assessment_title} Marks"
        self.post_content = f"# {assessment_title.title()}"
        self.post_content += f"\n{sec_role.mention} **Click the button(s)** below to show your"
        self.post_content += " marks. If you can't see your marks, [turn on your embed settings]"
        self.post_content += "(https://rtech.support/meta/discord-embeds/).\n"
        self.post_content += f"\n{faculty_text}\n" if faculty_text else ""
        self.post_content += "\n-# New buttons may show up for you to see"
        self.post_content += " further breakdown of your marks. But they will be"
        self.post_content += " only active for a few seconds after you press the buttons."
        # create and add button to view
        if not assessment_is_grade:
            self.add_item(ShowMarksButton(sec, assessment))
            return
        # add more buttons if this is grade
        buttons = {
            0: [
                MarksSprdsht.SecXX.GRADE_COL,
                MarksSprdsht.SecXX.THEORY_COL,
                MarksSprdsht.SecXX.LAB_COL,
            ],
            1: [
                MarksSprdsht.SecXX.ASSIGNMENT_COL,
                MarksSprdsht.SecXX.QUIZ_COL,
                MarksSprdsht.SecXX.MIDTERM_UNSCALED_COL,
                MarksSprdsht.SecXX.FINAL_UNSCALED_COL,
            ],
        }
        for row, assessments in buttons.items():
            style = hikari.ButtonStyle.DANGER if row == 0 else hikari.ButtonStyle.PRIMARY
            for assmnt in assessments:
                self.add_item(ShowMarksButton(sec, assmnt, label=assmnt, row=row, style=style))
